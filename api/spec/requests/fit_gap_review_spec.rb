require 'rails_helper'

RSpec.describe 'Fit/gap review access and lifecycle', type: :request do
  let!(:review) { create_review }
  let(:portfolio) { review.first }
  let(:vacancy) { review.last }
  let(:headers) { assessor_headers }
  let(:path) { "/api/v1/portfolios/#{portfolio.id}/fitgap" }

  before { add_requirement(vacancy); add_rating(portfolio) }

  it 'returns a durable pending report and enqueues only once on repeated requests' do
    2.times { post path, params: { vacancy_id: vacancy.id }, headers: headers }
    expect(response).to have_http_status(:accepted)
    expect(JSON.parse(response.body).dig('report', 'generation_status')).to eq('pending')
    expect(FitGapGeneratorWorker.jobs.length).to eq(1)
    expect(FitGapReport.where(portfolio: portfolio, vacancy: vacancy).count).to eq(1)
  end

  it 'requires authentication' do
    post path, params: { vacancy_id: vacancy.id }, headers: { 'X-Tenant-Scheme' => headers && 'spec-101' }
    expect(response).to have_http_status(:unauthorized)
    expect(FitGapGeneratorWorker.jobs).to be_empty
  end

  it 'rejects candidate roles' do
    post path, params: { vacancy_id: vacancy.id }, headers: assessor_headers(role: 'student')
    expect(response).to have_http_status(:forbidden)
  end

  it 'does not disclose or modify another tenant portfolio, including exports and overrides' do
    foreign_portfolio, = create_review(tenant_id: 202)
    foreign_skill = add_rating(foreign_portfolio)
    get "/api/v1/portfolios/#{foreign_portfolio.id}/export", params: { format: 'json' }, headers: headers
    expect(response).to have_http_status(:not_found)
    post "/api/v1/portfolios/#{foreign_portfolio.id}/fitgap", params: { vacancy_id: vacancy.id }, headers: headers
    expect(response).to have_http_status(:not_found)
    post "/api/v1/portfolio_skills/#{foreign_skill.id}/override", params: { override: { override_level: 4 } }, headers: headers
    expect(response).to have_http_status(:not_found)
    expect(foreign_skill.reload.assessor_override).to be_nil
    expect(FitGapGeneratorWorker.jobs).to be_empty
  end

  it 'rejects a vacancy from another tenant' do
    _, foreign_vacancy = create_review(tenant_id: 202)
    post path, params: { vacancy_id: foreign_vacancy.id }, headers: headers
    expect(response).to have_http_status(:not_found)
    expect(FitGapGeneratorWorker.jobs).to be_empty
  end

  it 'keeps the successful report on an override and marks it stale' do
    report = FitGap::Engine.new(portfolio: portfolio, vacancy: vacancy).call
    original = report.skill_comparisons
    skill = portfolio.portfolio_skills.first
    post "/api/v1/portfolio_skills/#{skill.id}/override", params: { override: { override_level: 4, assessor_notes: 'Synthetic review' } }, headers: headers
    expect(response).to have_http_status(:created)
    expect(report.reload.skill_comparisons).to eq(original)
    get "#{path}/#{vacancy.id}", headers: headers
    expect(JSON.parse(response.body).dig('report', 'generation_status')).to eq('stale')
  end

  it 'refuses an export that would present a stale comparison as current' do
    FitGap::Engine.new(portfolio: portfolio, vacancy: vacancy).call
    vacancy.vacancy_skills.first.update!(expected_level: 5)
    get "/api/v1/portfolios/#{portfolio.id}/export", params: { format: 'json', vacancy_id: vacancy.id }, headers: headers
    expect(response).to have_http_status(:conflict)
  end

  it 'rejects unknown tenant context' do
    token = JsonWebToken.encode(user_id: 1, role: 'admin', scheme: 'missing-organization')
    post path, params: { vacancy_id: vacancy.id }, headers: { 'Authorization' => "Bearer #{token}" }
    expect(response).to have_http_status(:forbidden)
  end
end
