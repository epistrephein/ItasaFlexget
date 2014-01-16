Itasa Flexget plugin (v 1.3.2, porting per Flexget 1.2)
==============================

- [Flexget](http://www.flexget.com) 
- [Itasa](http://italiansubs.net)
- [ItasaFlexget forum post on Itasa](http://www.italiansubs.net/forum/hardware-software/itasa-flexget-plugin/)

porting per Flexget 1.2 del plugin ItasaFlexget.
il codice è sostanzialmente identico, cambia solo l'interfacciamente con la nuova struttura dei plugin


Install
-------
Drop `ItasaFlexGet.py` in `~/.flexget/plugins`

Flexget compatibility
---------------------
tested with Flexget 1.2.37

Flexget config.yml examples
---------------------------

feeds:
  myitasa:
    rss: http://www.italiansubs.net/index.php?option=com_rsssub...  #myitasa or itasa subtitle feed
    accept_all: yes  #accept all from myitasa                                               
    itasa:
      username: itasaUsername
      password: itasaPassword
      path: ~/subtitle/download/folder # absolute or starting from $HOME

Features
---------------------------
* Extracted fields:
  * title
  * output _downloaded zip path_
  * series\_name _Itasa version_
  * series_season
  * series_episode

Test
----------------------------
`python2 -m unittest test`
Test will ask for itasa username and password

TODO : verify if still working