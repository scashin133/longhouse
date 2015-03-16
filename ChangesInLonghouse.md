# Changes in Longhouse from Google Code #

## Components removed from Google Code ##

The following components were removed from Google Code in October and November, 2007, by the original customer Jason Robbins due to being proprietary software and/or Google-specific hardware and software solutions:
  1. Big Table - Proprietary database tool used by Google to store all data
  1. Search engine - used Google indexing and search technology
  1. Web server
  1. E-mail service integration
  1. Downloads hosting on separate Google-owned file server
  1. All proprietary javascript

## Outside software packaged with Longhouse ##

This section documents software that either:
  * was not required or used by Google Code, but is used in Longhouse
  * was used in Google Code, and is still used in Longhouse but in a different manner.

### Software libraries used by Longhouse ###

  1. YAML: used to parse configuration settings, and used to generate business objects according to the specifications packaged with Longhouse. The business object generation process mirrors a technique used at Google to generate business objects, but the generator tool was written by the Longhouse team and provides extra features, namely the ability for generated objects to be serialized and deserialized using XML.
  1. Twisted: Twisted is used to replace the Google web server. In the future it will also serve as an SMTP server and an SMTP client implementation, replacing the Google e-mail service integration.
  1. Lucene: Lucene will be used to replace the search engine.

### Required by Longhouse ###

  1. Subversion: Although Google Code uses Subversion to control artifacts such as Wiki pages, Longhouse implements a new Subversion controller, providing a different way to use Subversion. This new Subversion controller is crucial to the ability of Longhouse to commit XML files representing business objects to Subversion servers.