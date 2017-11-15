#
# Class to execute barometer-manage db_sync
#
# == Parameters
#
# [*extra_params*]
#   (optional) String of extra command line parameters to append
#   to the barometer-dbsync command.
#   Defaults to undef
#
class barometer::db::sync(
  $extra_params  = undef,
) {
  exec { 'barometer-db-sync':
    command     => "barometer-manage db_sync ${extra_params}",
    path        => [ '/bin', '/usr/bin', ],
    user        => 'barometer',
    refreshonly => true,
    try_sleep   => 5,
    tries       => 10,
    logoutput   => on_failure,
    subscribe   => [Package['barometer'], Barometer_config['database/connection']],
  }

  Exec['barometer-manage db_sync'] ~> Service<| title == 'barometer' |>
}
