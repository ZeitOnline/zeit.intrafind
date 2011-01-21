Vivi Intrafind API
==================


Tagger
------


>>> content = XXX
>>> tagger = ITagger(content)


Initially there are no tags:

>>> tagger.by_type()
{}
>>> list(tagger)
[]


``update`` talks to tagger and tags the article

>>> tagger.update()


>>> tagger.by_type()
{'Location': [...],
 'topic': [...]}

>>> tagger['Berlin']
<Tag ...>


Blacklisting a tag removes it from XML:

>>> tagger['Berlin'].blacklisted = True

... no longer in xml ...

>>> tagger['Berlin'].blacklisted = False

... again in xml ...


Edgecases -> unittest

* Blacklisting survives update (even when the tag isn't in the result for
  a while)
* delete / add not possible (only via update)



Tags as they are stored in DAV
------------------------------

Searchable, summarizable

