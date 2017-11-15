# == Class: barometer::policy
#
# Configure the barometer policies
#
# === Parameters
#
# [*policies*]
#   (optional) Set of policies to configure for barometer
#   Example :
#     {
#       'barometer-context_is_admin' => {
#         'key' => 'context_is_admin',
#         'value' => 'true'
#       },
#       'barometer-default' => {
#         'key' => 'default',
#         'value' => 'rule:admin_or_owner'
#       }
#     }
#   Defaults to empty hash.
#
# [*policy_path*]
#   (optional) Path to the nova policy.json file
#   Defaults to /etc/barometer/policy.json
#
class barometer::policy (
  $policies    = {},
  $policy_path = '/etc/barometer/policy.json',
) {

  validate_hash($policies)

  Openstacklib::Policy::Base {
    file_path => $policy_path,
  }

  create_resources('openstacklib::policy::base', $policies)

  oslo::policy { 'barometer_config': policy_file => $policy_path }

}
