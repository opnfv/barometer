#
# Unit tests for barometer::keystone::auth
#

require 'spec_helper'

describe 'barometer::keystone::auth' do
  shared_examples_for 'barometer-keystone-auth' do
    context 'with default class parameters' do
      let :params do
        { :password => 'barometer_password',
          :tenant   => 'foobar' }
      end

      it { is_expected.to contain_keystone_user('barometer').with(
        :ensure   => 'present',
        :password => 'barometer_password',
      ) }

      it { is_expected.to contain_keystone_user_role('barometer@foobar').with(
        :ensure  => 'present',
        :roles   => ['admin']
      )}

      it { is_expected.to contain_keystone_service('barometer::nfv-orchestration').with(
        :ensure      => 'present',
        :description => 'barometer NFV orchestration Service'
      ) }

      it { is_expected.to contain_keystone_endpoint('RegionOne/barometer::nfv-orchestration').with(
        :ensure       => 'present',
        :public_url   => 'http://127.0.0.1:9890',
        :admin_url    => 'http://127.0.0.1:9890',
        :internal_url => 'http://127.0.0.1:9890',
      ) }
    end

    context 'when overriding URL parameters' do
      let :params do
        { :password     => 'barometer_password',
          :public_url   => 'https://10.10.10.10:80',
          :internal_url => 'http://10.10.10.11:81',
          :admin_url    => 'http://10.10.10.12:81', }
      end

      it { is_expected.to contain_keystone_endpoint('RegionOne/barometer::nfv-orchestration').with(
        :ensure       => 'present',
        :public_url   => 'https://10.10.10.10:80',
        :internal_url => 'http://10.10.10.11:81',
        :admin_url    => 'http://10.10.10.12:81',
      ) }
    end

    context 'when overriding auth name' do
      let :params do
        { :password => 'foo',
          :auth_name => 'barometery' }
      end

      it { is_expected.to contain_keystone_user('barometery') }
      it { is_expected.to contain_keystone_user_role('barometery@services') }
      it { is_expected.to contain_keystone_service('barometer::nfv-orchestration') }
      it { is_expected.to contain_keystone_endpoint('RegionOne/barometer::nfv-orchestration') }
    end

    context 'when overriding service name' do
      let :params do
        { :service_name => 'barometer_service',
          :auth_name    => 'barometer',
          :password     => 'barometer_password' }
      end

      it { is_expected.to contain_keystone_user('barometer') }
      it { is_expected.to contain_keystone_user_role('barometer@services') }
      it { is_expected.to contain_keystone_service('barometer_service::nfv-orchestration') }
      it { is_expected.to contain_keystone_endpoint('RegionOne/barometer_service::nfv-orchestration') }
    end

    context 'when disabling user configuration' do

      let :params do
        {
          :password       => 'barometer_password',
          :configure_user => false
        }
      end

      it { is_expected.not_to contain_keystone_user('barometer') }
      it { is_expected.to contain_keystone_user_role('barometer@services') }
      it { is_expected.to contain_keystone_service('barometer::nfv-orchestration').with(
        :ensure      => 'present',
        :description => 'barometer NFV orchestration Service'
      ) }

    end

    context 'when disabling user and user role configuration' do

      let :params do
        {
          :password            => 'barometer_password',
          :configure_user      => false,
          :configure_user_role => false
        }
      end

      it { is_expected.not_to contain_keystone_user('barometer') }
      it { is_expected.not_to contain_keystone_user_role('barometer@services') }
      it { is_expected.to contain_keystone_service('barometer::nfv-orchestration').with(
        :ensure      => 'present',
        :description => 'barometer NFV orchestration Service'
      ) }

    end

    context 'when using ensure absent' do

      let :params do
        {
          :password => 'barometer_password',
          :ensure   => 'absent'
        }
      end

      it { is_expected.to contain_keystone__resource__service_identity('barometer').with_ensure('absent') }

    end
  end

  on_supported_os({
    :supported_os => OSDefaults.get_supported_os
  }).each do |os,facts|
    context "on #{os}" do
      let (:facts) do
        facts.merge!(OSDefaults.get_facts())
      end

      it_behaves_like 'barometer-keystone-auth'
    end
  end
end
