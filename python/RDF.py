# 
# RDF.py - Redland Python RDF module
#
# $Id$
#
# Copyright (C) 2000-2001 David Beckett - http://purl.org/net/dajobe/
# Institute for Learning and Research Technology - http://www.ilrt.org/
# University of Bristol - http://www.bristol.ac.uk/
# 
# This package is Free Software or Open Source available under the
# following licenses (these are alternatives):
#   1. GNU Lesser General Public License (LGPL)
#   2. GNU General Public License (GPL)
#   3. Mozilla Public License (MPL)
# 
# See LICENSE.html or LICENSE.txt at the top of this package for the
# full license terms.
# 
# 
#

__version__ = "0.2"

__debug__ = 0

__world__ = None

import sys
import string

import Redland;


class world:
  """Core RDF class"""

  def __init__(self,digest_name="",uri_hash=None):
    """Create new RDF World object (constructor)"""
    self.world=Redland.librdf_new_world()
    Redland.librdf_world_open(self.world)

    # Keep a circular reference to this object so it is deleted last
    self.me=self

    global __world__
    __world__=self

  # __init__ ()

  def close(self):
    """Destroy RDF World object (destructor)."""
    if __debug__:
      print "Destroying RDF.world"
    self.me=None
    Redland.librdf_free_world(self.world)

  def debug(self,value=0):
    global __debug__
    if value:
      __debug__=value
    else:
      return __debug__


# end class world


class node:

  # CONSTRUCTOR
  def __init__(self, args={}):
    """Create an RDF Node (constructor)."""
    if __debug__:
      print "Creating RDF.node args=",args
    self.node=None
    self.free_me=1

    if args.has_key('uri_string'):
      self.node=Redland.librdf_new_node_from_uri_string(__world__.world, args['uri_string'])
    elif args.has_key('uri'):
      self.node=Redland.librdf_new_node_from_uri(args['uri'].uri)
    elif args.has_key('literal'):
      if args.has_key('xml_language'):
        xml_language=args['xml_language']
      else:
        xml_language=""
      if args.has_key('xml_space'):
        xml_space=args['xml_space']
      else:
        xml_space=0
      if args.has_key('is_wf_xml'):
        is_wf_xml=args['is_wf_xml']
      else:
        is_wf_xml=0
      self.node=Redland.librdf_new_node_from_literal(__world__.world, args['literal'],xml_language,xml_space,is_wf_xml)
    elif args.has_key('node'):
      self.node=Redland.librdf_new_node_from_node(args['node'].node)
    elif args.has_key('from_object'):
      # internal constructor to build an object from a node created
      # by librdf e.g. from the result of a iterator->next operation
      # this is always shared (at present) so should not be freed
      self.node=args['from_object']
      self.free_me=args['free_node']
    else:
      self.node=Redland.librdf_new_node(__world__.world)

  # DESTRUCTOR
  def __del__(self):
    """Free an RDF Node (destructor)."""
    if __debug__:
      print "Destroying RDF.node"
    if self.node and self.free_me:
      if __debug__:
        print "Deleting Redland node object"
      Redland.librdf_free_node(self.node)

  def uri (self, uri=None):
    """Set/get the node URI."""
    if not uri:
      return Redland.librdf_node_get_uri(self.node)

    return Redland.librdf_node_set_uri(self.node, uri.uri)

  def type (self, type=None):
    """Set/get the node type."""
    if not type:
      return Redland.librdf_node_get_type(self.node)

    return Redland.librdf_node_set_type(self.node, type)

  def literal_value(self):
    """Get a literal node string value."""
    return Redland.librdf_node_get_literal_value(self.node)

  def literal_value_language(self):
    """Get a literal node language value."""
    return Redland.librdf_node_get_literal_value_language(self.node)

  def literal_value_xml_space(self):
    """Get a literal node XML space value."""
    return Redland.librdf_node_get_literal_value_xml_space(self.node)

  def literal_value_is_wf_xml(self):
    """Get a literal node is WF XML value."""
    return Redland.librdf_node_get_literal_value_is_wf_xml(self.node)

  def set_literal_value (self,value,xml_language,xml_space,is_wf_xml):
    """Set a literal node string value."""
    return Redland.librdf_node_set_literal_value(self.node,value,xml_language,xml_space,is_wf_xml)

  def __str__(self):
    """Get a string representation of an RDF Node."""
    return Redland.librdf_node_to_string(self.node)

  def equals(self,node):
    """Compare RDF Node to another RDF Node."""
    return Redland.librdf_node_equals(self.node, node.node)

# end class node


class statement:

  # CONSTRUCTOR
  def __init__(self, args={}):
    """Create an RDF Statement (constructor)."""
    if __debug__:
      print "Creating RDF.statement object args",args
    self.statement=None
    self.free_me=1

    if args.has_key('statement'):
      self.statement=Redland.librdf_new_statement_from_statement(args['statement'].statement)
    elif args.has_key('subject'):
      subject=args['subject']
      predicate=args['predicate']
      object=args['object']

      # Replace python-land 'None' with C-land 'NULL' pointers to Redland.librdf_node
      if not subject:
	s=None
      else:
	s=subject.node

      if not predicate:
	p=None
      else:
	p=predicate.node

      if not object:
	o=None
      else:
	o=object.node

      self.statement=Redland.librdf_new_statement_from_nodes(__world__.world, s, p, o)

      # Zap the incoming librdf node objects since they are now owned by the
      # librdf statement object self.statement
      if subject:
	subject.node=None
      if predicate:
	predicate.node=None
      if object:
	object.node=None

    elif args.has_key('from_object') and args.has_key('free_statements'): 
      # internal constructor to build an object from a statement created
      # by librdf e.g. from the result of a stream.next operation
      self.statement=args['from_object']
      self.free_me=args['free_statements']

    else:
      self.statement=Redland.librdf_new_statement(__world__.world)

  # DESTRUCTOR
  def __del__(self):
    if __debug__:
      print "Destroying RDF.statement"
    if self.statement and self.free_me:
      if __debug__:
        print "Deleting Redland statement object"
      Redland.librdf_free_statement(self.statement)

  def subject (self,subject=None):
    if subject:
      return Redland.librdf_statement_get_subject(self.statement)

    # Zap the incoming librdf node object since it is now owned by the
    # librdf statement object self.statement
    subject.node=None
    return Redland.librdf_statement_set_subject(self.statement,subject)

  def predicate (self,predicate=None):
    if predicate:
      return Redland.librdf_statement_get_predicate(self.statement)

    # Zap the incoming librdf node object since it is now owned by the
    # librdf statement object self.statement
    predicate.node=None
    return Redland.librdf_statement_set_predicate(self.statement,predicate)

  def object (self):
    if object:
      return Redland.librdf_statement_get_object(self.statement)

    # Zap the incoming librdf node object since it is now owned by the
    # librdf statement object self.statement
    object.node=None
    return Redland.librdf_statement_set_object(self.statement,object)

  def __str__ (self):
    return Redland.librdf_statement_to_string(self.statement)

# end class statement


class model:

  # CONSTRUCTOR
  def __init__(self, storage, args={}):
    """Create an RDF Model (constructor)."""
    if __debug__:
      print "Creating RDF.model args=",args
    self.model=None
    self.storage=None

    if args.has_key('options_string'):
      self.model=Redland.librdf_new_model(__world__.world, storage.storage, args['options_string'])
    elif args.has_key('options_hash'):
      self.model=Redland.librdf_new_model_with_options(__world__.world, storage.storage, args['options_hash'].hash)
    elif args.has_key('model'):
      self.model=Redland.librdf_new_model_from_model(storage.storage,
      args['model'].model)
    else:
      self.model=Redland.librdf_new_model(__world__.world, storage.storage, "")

    if self.model == "NULL":
      self.model=None
      raise "new RDF.model failed"
    else:
      # keep a reference around so storage object is destroyed after this
      self.storage=storage

  # DESTRUCTOR
  def __del__(self):
    if __debug__:
      print "Destroying RDF.model "
    if self.model:
      Redland.librdf_free_model(self.model)

  def size(self):
    return Redland.librdf_model_size(self.model)

  def add(self,subject,predicate,object):
    return Redland.librdf_model_add(self.model, subject.node, predicate.node, object.node);

  def add_string_literal_statement (self,subject,predicate,string,xml_language,xml_space,is_wf_xml):
    return Redland.librdf_model_add_string_literal_statement(self.model, subject.node, predicate.node, string, xml_language, xml_space, is_wf_xml)

  def add_statement (self,statement):
    Redland.librdf_model_add_statement(self.model,statement.statement)

  def add_statements (self,statement_stream):
    return Redland.librdf_model_add_statements(self.model, statement_stream.stream)

  def remove_statement (self,statement):
    return Redland.librdf_model_remove_statement(self.model, statement.statement)

  def contains_statement (self,statement):
    return Redland.librdf_model_contains_statement(self.model, statement.statement)

  def serialise (self):
    my_stream=Redland.librdf_model_serialise(self.model)
    return stream(my_stream,self,1)

  def find_statements (self,statement):
    my_stream=Redland.librdf_model_find_statements(self.model, statement.statement)
    return stream(my_stream,self,0)

  # FIXME: Must add versions of get_sources/arcs/targets
  # returning python lists of node objects

  def get_sources_iterator (self,arc,target):
    my_iterator=Redland.librdf_model_get_sources(self.model, arc.node, target.node)
    return iterator(my_iterator,self)

  def get_arcs_iterator (self,source,target):
    my_iterator=Redland.librdf_model_get_arcs(self.model, source.node, target.node)
    return iterator(my_iterator,self)

  def get_targets_iterator (self,source,arc):
    my_iterator=Redland.librdf_model_get_targets(self.model, source.node, arc.node)
    return iterator(my_iterator,self)

  def get_source (self,arc,target):
    my_node=Redland.librdf_model_get_source(self.model, arc.node, target.node)
    if not my_node:
      return None
    else:
      return node({"from_object" : my_node, "free_node" : 1})

  def get_arc (self,source,target):
    my_node=Redland.librdf_model_get_arc(self.model, source.node, target.node)
    if not my_node:
      return None
    else:
      return node({"from_object" : my_node, "free_node" : 1})

  def get_target (self,source,arc):
    my_node=Redland.librdf_model_get_target(self.model, source.node, arc.node)
    if not my_node:
      return None
    else:
      return node({"from_object" : my_node, "free_node" : 1})

#end class model


class iterator:

  # CONSTRUCTOR
  def __init__(self,object,creator):
    """Create an RDF Iterator (constructor)."""
    if __debug__:
      print "Creating RDF.iterator object=",object,"creator=",creator
    self.iterator=object;
    # Keep around a reference to the object that created the iterator
    # so that python does not destroy us before them.
    self.creator=creator;

  # DESTRUCTOR
  def __del__(self):
    if __debug__:
      print "Destroying RDF.iterator"
    Redland.librdf_free_iterator(self.iterator)

  def have_elements (self):
    return Redland.librdf_iterator_have_elements(self.iterator)

  def next (self):
    my_node=Redland.librdf_iterator_get_next(self.iterator)
    if my_node == "NULL":
      return None
    # return a new (1) node (2)owned by the librdf iterator object
    # Reasons: (1) at the user API level the iterator only returns nodes
    #          (2) the node returned is shared with the iterator
    return node({"from_object" : my_node})

#end class iterator


class stream:

  # CONSTRUCTOR
  def __init__(self, object, creator, free_statements):
    """Create an RDF Stream (constructor)."""
    if __debug__:
      print "Creating RDF.stream for object",object,"creator",creator,"free_statements",free_statements

    self.stream=object;
    # Keep around a reference to the object that created the stream
    # so that perl does not destroy us before them.
    self.creator=creator;
    # should the resulting statements be freed?
    self.free_statements=free_statements;

  # DESTRUCTOR
  def __del__(self):
    if __debug__:
      print "Destroying RDF.stream"
    Redland.librdf_free_stream(self.stream)

  def end (self):
    if not self.stream:
      return 1
    return Redland.librdf_stream_end(self.stream)

  def next (self):
    if not self.stream:
      return None
    # return a new statement created by the librdf stream object
    my_statement=Redland.librdf_stream_next(self.stream)
    if my_statement == "NULL":
      return None
    return statement({"from_object" : my_statement, "free_statements" : self.free_statements})

# end class stream


class storage:

  # CONSTRUCTOR
  def __init__(self, args):
    """Create an RDF Storage (constructor)."""
    if __debug__:
      print "Creating RDF.storage args=",args
    self.storage=None

    if args.has_key('storage_name') and args.has_key('name') and args.has_key('options_string'):
      self.storage=Redland.librdf_new_storage(__world__.world, args['storage_name'] ,args['name'], args['options_string']);
    elif args.has_key('storage'):
      self.storage=Redland.librdf_new_storage_from_storage(args['storage'].storage);
    else:
      raise "new RDF.storage failed - illegal arguments"

    if self.storage == "NULL":
      self.storage=None
      raise "new RDF.storage failed"


  # DESTRUCTOR
  def __del__(self):
    if __debug__:
      print "Destroying RDF.storage"
    if self.storage:
      Redland.librdf_free_storage(self.storage)

# end class storage


class uri:

  # CONSTRUCTOR
  def __init__(self, args):
    """Create an RDF Uri (constructor)."""
    if __debug__:
      print "Creating RDF.uri args=",args
    self.uri=None

    if args.has_key('string'):
     self.uri=Redland.librdf_new_uri(__world__.world, string)
    elif args.has_key('uri'):
      # FIXME: If the URI is a python URI ... need to use the above constructor
      # if isa(uri, <python uri object>):
      #   self.uri=Redland.librdf_new_uri(__world__.world, uri.as_string)
      self.uri=Redland.librdf_new_uri_from_uri(uri.uri)

  # DESTRUCTOR
  def __del__(self):
    if __debug__:
      print "Destroying RDF.uri"
    if self.uri:
      Redland.librdf_free_uri(self.model)

  def __str__(self):
    """Get a string representation of an RDF URI."""
    return Redland.librdf_uri_to_string(self.uri)

  def equals(self,uri):
    """Compare RDF URI to another RDF URI."""
    return Redland.librdf_uri_equals(self.uri, uri.uri)

# end class uri


class parser:

  # CONSTRUCTOR
  def __init__(self, name, mime_type="", uri=None):
    """Create an RDF Parser (constructor)."""
    if __debug__:
      print "Creating RDF.parser name=",name,"mime_type=",mime_type,"uri=",uri

    if uri:
      uri=uri.uri
  
    self.parser=Redland.librdf_new_parser(__world__.world, name,mime_type,uri)

  # DESTRUCTOR
  def __del__(self):
    if __debug__:
      print "Destroying RDF.parser"
    if self.parser:
      Redland.librdf_free_parser(self.parser)

  def parse_as_stream (self,uri,base_uri):
    my_stream=Redland.librdf_parser_parse_as_stream(self.parser,uri.uri, base_uri.uri)
    return stream(my_stream,self,1)

  def parse_into_model (self,uri,base_uri,model):
    return Redland.librdf_parser_parse_into_model(self.parser,uri.uri,base_uri.uri,model.model)

  def feature (self,uri,value=None):
    # FIXME: if uri not <an RDF.uri object>:
    #  uri=uri({'string'} : uri_string})  

    if not value:
      return Redland.librdf_parser_get_feature(self.parser,uri.uri)

    return Redland.librdf_parser_set_feature(self.parser,uri.uri,value)

# end class parser
