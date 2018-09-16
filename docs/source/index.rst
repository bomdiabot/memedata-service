.. memedata documentation master file, created by
   sphinx-quickstart on Sat Sep 15 23:38:14 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Welcome to memedata's documentation!
====================================
**Memedata** is `bomdiabot`_'s service responsible for providing
text and image data for memes.
Everything is obtained via a REST API, which is described here.

The project's repo can be found `here`_.

.. _bomdiabot: http://consagrado.xyz
.. _here: https://github.com/bomdiabot/memedata-service

===========
API Summary
===========

.. qrefflask:: memedata.app:get_app()
	:undoc-static:



===========
API Details
===========

.. autoflask:: memedata.app:get_app()
	:undoc-static:
