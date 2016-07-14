if $operatingsystem == 'Ubuntu' {
    package { 'collectd':
        ensure => installed,
    }
}
