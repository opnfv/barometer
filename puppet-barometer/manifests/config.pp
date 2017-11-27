# == Class: barometer::config
#
# This class is used to manage arbitrary barometer configurations.
#
# === Parameters
#
# [*barometer_config*]
#   (optional) Allow configuration of arbitrary barometer configurations.
#   The value is an hash of barometer_config resources. Example:
#   { 'DEFAULT/foo' => { value => 'fooValue'},
#     'DEFAULT/bar' => { value => 'barValue'}
#   }
#   In yaml format, Example:
#   barometer_config:
#     DEFAULT/foo:
#       value: fooValue
#     DEFAULT/bar:
#       value: barValue
#
#   NOTE: The configuration MUST NOT be already handled by this module
#   or Puppet catalog compilation will fail with duplicate resources.
#
class barometer::config (
  $barometer_config = {},
) {

  validate_hash($barometer_config)

  create_resources('barometer_config', $barometer_config)
}
