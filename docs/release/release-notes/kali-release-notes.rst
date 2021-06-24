.. This work is licensed under a Creative Commons Attribution 4.0 International License.
.. http://creativecommons.org/licenses/by/4.0

============================
Barometer Kali Release Notes
============================

This document provides the release notes for Kali release of Barometer.

Summary
-------
The Kali release is the first one since becoming part of Anuket, and focussed
on changes that will make testing and integrating easier.

Details
-------
Testing and build tools were developed and updated to do the following:

* A new reference container was added for the collectd-6.0 version, which is
  under development and represents a big API change that is not backwards
  compatible. This reference build should facilitate porting the plugins that
  were previously developed by the Barometer project.
  https://jira.anuket.io/browse/BAROMETER-184

* Updated to the stable version of collectd to collectd 5.12.

* Removed duplication in the three existing containers (stable, latest and experimental).
  https://jira.anuket.io/browse/BAROMETER-179

Some work was started but not completed in the Kali release:

* Updating of the ansible playbooks for generating configs so that they will be
  easier to maintain and extend in the future.

* Additional testing tools for verifying plugin functionality

References
----------
* `Barometer Kali release plan <https://wiki.anuket.io/display/HOME/Barometer+Kali+Release+Planning>`_
* `Kali Release on Jira <https://jira.anuket.io/projects/BAROMETER/versions/10224>`_
