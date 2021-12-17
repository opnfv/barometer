.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0
.. (c) Anuket and others.

============================
Lakelse Release Notes
============================

.. _Release Notes_lakelse:

Lakelse
=======

.. _Release Notes_lakelse_Release Summary:

Release Summary
---------------

.. docs/release/release-notes/notes/lakelse/add_unix_sock-e29efe16156c5c8e.yaml @ None

Added unixsock plugin to one-click install.


.. docs/release/release-notes/notes/lakelse/ansible-build-containers-b4a4cc9cb70f83b3.yaml @ None

Add ansible playbook for building the containers locally.


.. docs/release/release-notes/notes/lakelse/anuket_containers-21b4206cb26c9975.yaml @ None

Since the anuket dockerhub repository was created, and containers are being pushed to there, instructions and build scripts have been updated to reflect this.


.. docs/release/release-notes/notes/lakelse/collectd-5-v-6-testing-cc821b32bad2794c.yaml @ None

Testing playbooks were added to compare collectd5 vs collectd6, for the purpose of helping to review new PRs by comparing the generated metrics between versions.


.. docs/release/release-notes/notes/lakelse/remove_dpdk_stats_events_plugins-59f366855f6e4261.yaml @ None

Remove dpdkstats and dpdkevents from Barometer.


.. docs/release/release-notes/notes/lakelse/update_logparser_config-0db3d2746e6ad582.yaml @ None

Enable the Logparser plugin by default when using one-click install.


.. _Release Notes_lakelse_Testing Notes:

Testing Notes
-------------

.. docs/release/release-notes/notes/lakelse/collectd-5-v-6-testing-cc821b32bad2794c.yaml @ None

- Added a playbook to compare collectd 5 and collectd 6. The playbook uses
  existing ansible roles to build both collectd 5 and collectd 6 container
  images, creates a common configuration, then runs the containers and shows
  the outputs to let the user inspect the metrics and whether they match.


.. _Release Notes_lakelse_Documentation Updates:

Documentation Updates
---------------------

.. docs/release/release-notes/notes/lakelse/anuket_containers-21b4206cb26c9975.yaml @ None

- Docs have been updated to use anuket/ repository in dockerhub.
  Container build instructions now use anuket/ prefix to tag images.


.. _Release Notes_lakelse_Container updates:

Container updates
-----------------

.. docs/release/release-notes/notes/lakelse/anuket_containers-21b4206cb26c9975.yaml @ None

- Containers are now pulled from anuket/ repository in dockerhub.

.. docs/release/release-notes/notes/lakelse/collectd-6-testing-flask-app-2bb0ca1326775dd8.yaml @ None

- Add a flask app for testing collectd using metrics sent via write_http plugin.

.. docs/release/release-notes/notes/lakelse/update-grafana-9bee82ecfa11f54a.yaml @ None

- Grafana container was updated to support both jiffies and percent for cpu metrics.


.. _Release Notes_lakelse_Ansible playbook updates:

Ansible playbook updates
------------------------

.. docs/release/release-notes/notes/lakelse/add_unix_sock-e29efe16156c5c8e.yaml @ None

- Added `unixsock <https://collectd.org/documentation/manpages/collectd-unixsock.5.shtml>`_
  plugin to one-click install, which allows the user to interact with collectd using the
  ``collectdctl`` command in the bar-collectd-* containers.
  The unixsock plugin is useful for debugging issues in collectd, and can
  be used to verify that metrics are being collected without having to
  create CSV files or log into the container.

.. docs/release/release-notes/notes/lakelse/ansible-build-containers-b4a4cc9cb70f83b3.yaml @ None

- Added a playbook and role for building the collectd containers locally.
  This automates the actions described in the docker install guide. The
  ``barometer-collectd``, ``barometer-collectd-latest`` and the
  ``barometer-collectd-experimental`` containers are now easier to build
  locally. The ``barometer-collectd-6`` and
  ``barometer-collectd-experimental`` containers can also be built with
  arbirtary PRs applied, to aid in testing locally.

.. docs/release/release-notes/notes/lakelse/anuket_containers-21b4206cb26c9975.yaml @ None

- Containers are now pulled from anuker/ repository in dockerhub.

.. docs/release/release-notes/notes/lakelse/update_logparser_config-0db3d2746e6ad582.yaml @ None

- The logparser plugin is now rendered for all flavours.
  The Logparser plugin has been part of collectd since 5.11, however, the ansible playbooks had it marked as experimental, and would not deploy it by default.


.. _Release Notes_lakelse_Build script updates:

Build script updates
--------------------

.. docs/release/release-notes/notes/lakelse/update-apply-pr-script-46e6d547d331c5f2.yaml @ None

- Update collectd_apply_pull_request.sh to rebase only if multiple chanegs are selected. The script will checkout the PR branch if there's only one PR_ID passed.


.. _Release Notes_lakelse_Normal Bug Fixes:

Normal Bug Fixes
----------------

.. docs/release/release-notes/notes/lakelse/update-grafana-9bee82ecfa11f54a.yaml @ None

- Update the grafana dashboard to show metrics in both jffies and percent, depending on what is configured.


.. _Release Notes_lakelse_Deprecations:

Deprecations
------------

.. docs/release/release-notes/notes/lakelse/remove_dpdk_stats_events_plugins-59f366855f6e4261.yaml @ None

- The dpdkstats and dpdkevents plugins were removed from Barometer. These
  plugins are still available in collectd, however, will not be deployed by
  Barometer. It is recommended that the DPDK telemetry plugin be used instead.


.. _Release Notes_lakelse_Other Notes:

Other Notes
-----------

.. docs/release/release-notes/notes/lakelse/add-reno-12eb20e3448b663b.yaml @ None

- Add `reno <https://docs.openstack.org/reno/latest/index.html#>`_ and corresponding tox jobs (compile notes and add new notes) to make compiling release notes easier
