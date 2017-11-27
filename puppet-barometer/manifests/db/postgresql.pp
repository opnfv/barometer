# == Class: barometer::db::postgresql
#
# Class that configures postgresql for barometer
# Requires the Puppetlabs postgresql module.
#
# === Parameters
#
# [*password*]
#   (Required) Password to connect to the database.
#
# [*dbname*]
#   (Optional) Name of the database.
#   Defaults to 'barometer'.
#
# [*user*]
#   (Optional) User to connect to the database.
#   Defaults to 'barometer'.
#
#  [*encoding*]
#    (Optional) The charset to use for the database.
#    Default to undef.
#
#  [*privileges*]
#    (Optional) Privileges given to the database user.
#    Default to 'ALL'
#
# == Dependencies
#
# == Examples
#
# == Authors
#
# == Copyright
#
class barometer::db::postgresql(
  $password,
  $dbname     = 'barometer',
  $user       = 'barometer',
  $encoding   = undef,
  $privileges = 'ALL',
) {

  Class['barometer::db::postgresql'] -> Service<| title == 'barometer' |>

  ::openstacklib::db::postgresql { 'barometer':
    password_hash => postgresql_password($user, $password),
    dbname        => $dbname,
    user          => $user,
    encoding      => $encoding,
    privileges    => $privileges,
  }

  ::Openstacklib::Db::Postgresql['barometer'] ~> Exec<| title == 'barometer-manage db_sync' |>

}
