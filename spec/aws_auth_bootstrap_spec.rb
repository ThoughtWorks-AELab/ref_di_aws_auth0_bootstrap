require 'spec_helper'

describe iam_policy('power_user') do
  it { should exist }
  it { should be_attachable }
  it { should be_attached_to_role('dev_admin') }
end

describe iam_policy('readonly') do
  it { should exist }
  it { should be_attachable }
  it { should be_attached_to_role('infra_reader') }
end


#TODO: saml_provider exists

