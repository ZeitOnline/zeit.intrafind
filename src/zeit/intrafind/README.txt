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

For a xml snippet like this::

    <tag freq="1" id="Karen+Duve" status="known" type="Person">
      Karen Duve
    </tag>

The following properties in DAV will be created::

    {http://namespaces.zeit.de/CMS/tagging/Karen+Duve}text = Karen Duve
    {http://namespaces.zeit.de/CMS/tagging/Karen+Duve}frequency = 1
    {http://namespaces.zeit.de/CMS/tagging/Karen+Duve}status = known
    {http://namespaces.zeit.de/CMS/tagging/Karen+Duve}type = Person

