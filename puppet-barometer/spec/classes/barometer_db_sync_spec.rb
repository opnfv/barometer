require 'spec_helper'

describe 'barometer::db::sync' do

  shared_examples_for 'barometer-dbsync' do

    it 'runs barometer-db-sync' do
      is_expected.to contain_exec('barometer-db-sync').with(
        :command     => 'barometer-manage db_sync ',
        :path        => [ '/bin', '/usr/bin', ],
        :refreshonly => 'true',
        :user        => 'barometer',
        :logoutput   => 'on_failure'
      )
    end

  end

  on_supported_os({
    :supported_os   => OSDefaults.get_supported_os
  }).each do |os,facts|
    context "on #{os}" do
      let (:facts) do
        facts.merge(OSDefaults.get_facts({
          :os_workers     => 8,
          :concat_basedir => '/var/lib/puppet/concat'
        }))
      end

      it_configures 'barometer-dbsync'
    end
  end

end
