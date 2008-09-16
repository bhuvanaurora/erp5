##############################################################################
# -*- coding: utf8 -*-
#
# Copyright (c) 2008 Nexedi SA and Contributors. All Rights Reserved.
#          Łukasz Nowak <lukasz.nowak@ventis.com.pl>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
##############################################################################

import unittest

from Products.ERP5Type.tests.ERP5TypeTestCase import ERP5TypeTestCase
from zLOG import LOG
from Products.ERP5Type.tests.Sequence import SequenceList
from Products.CMFCore.utils import getToolByName

from Products.ERP5.tests.testOrder import TestOrderMixin

class TestOrderBuilderMixin(TestOrderMixin):

  run_all_test = 1

  order_builder_portal_type = 'Order Builder'

  order_module = 'purchase_order_module'
  order_portal_type = 'Purchase Order'
  order_line_portal_type = 'Purchase Order Line'
  order_cell_portal_type = 'Purchase Order Cell'

  packing_list_portal_type = 'Internal Packing List'
  packing_list_line_portal_type = 'Internal Packing List Line'
  packing_list_cell_portal_type = 'Internal Packing List Cell'

  # hardcoded values
  order_builder_hardcoded_time_diff = 10.0

  # defaults
  decrease_quantity = 1.0
  max_delay = 0.0
  min_flow = 0.0

  def stepClearActivities(self, sequence=None, sequence_list=None,
                          **kw):
    """
    Clear activity tables
    """
    activity_tool = self.getPortal().portal_activities
    activity_tool.manageClearActivities(keep=0)

  def stepSetMaxDelayOnResource(self, sequence=None, sequence_list=None,
                          **kw):
    """
    Sets max_delay on resource
    """
    resource = sequence.get('resource')

    resource.edit(
      max_delay = self.max_delay,
    )

  def stepSetMinFlowOnResource(self, sequence=None, sequence_list=None,
                          **kw):
    """
    Sets min_flow on resource
    """
    resource = sequence.get('resource')

    resource.edit(
      min_flow = self.min_flow,
    )

  def stepFillOrderBuilder(self, sequence=None, sequence_list=None,
                          **kw):
    """
    Fills Order Builder with proper quantites
    """
    order_builder = sequence.get('order_builder')
    organisation = sequence.get('organisation')

    order_builder.edit(
      delivery_module = self.order_module,
      delivery_portal_type = self.order_portal_type,
      delivery_line_portal_type = self.order_line_portal_type,
      delivery_cell_portal_type = self.order_cell_portal_type,

      destination_value = organisation,

      resource_portal_type = self.resource_portal_type,
    )

    order_builder.newContent(
      portal_type = 'Category Movement Group',
      collect_order_group='delivery',
      tested_property=['source', 'destination',
                       'source_section', 'destination_section'],
      int_index=1
      )
    order_builder.newContent(
      portal_type = 'Property Movement Group',
      collect_order_group='delivery',
      tested_property=['start_date', 'stop_date'],
      int_index=2
      )

    order_builder.newContent(
      portal_type = 'Category Movement Group',
      collect_order_group='line',
      tested_property=['resource'],
      int_index=1
      )
    order_builder.newContent(
      portal_type = 'Base Variant Movement Group',
      collect_order_group='line',
      int_index=2
      )

    order_builder.newContent(
      portal_type = 'Variant Movement Group',
      collect_order_group='cell',
      int_index=1
      )

  def stepCheckGeneratedDocumentListVariated(self, sequence=None, sequence_list=None,
                          **kw):
    """
    Checks documents generated by Order Builders with its properties for variated resource
    """
    # XXX: Some values still hardcoded
    organisation = sequence.get('organisation')
    resource = sequence.get('resource')

    generated_document_list = sequence.get('generated_document_list')

    self.assertEquals(
      1, # XXX
      len(generated_document_list)
    )

    order = generated_document_list[0]

    self.assertEquals(
      order.getDestinationValue(),
      organisation
    )

    self.assertEquals(
      order.getStartDate(),
      self.wanted_start_date
    )

    self.assertEquals(
      order.getStopDate(),
      self.wanted_stop_date
    )

    order_line_list = order.contentValues(filter={'portal_type':self.order_line_portal_type})
    self.assertEquals(
      1, # XXX
      len(order_line_list)
    )

    order_line = order_line_list[0] # XXX: add support for more lines and cells too

    self.assertEquals(
      order_line.getResourceValue(),
      resource
    )

    self.assertEquals(
      order_line.getTotalQuantity(),
      sum(self.wanted_quantity_matrix.itervalues())
    )

    order_cell_list = order_line.contentValues(filter={'portal_type':self.order_cell_portal_type})
    self.assertEquals(
      len(order_cell_list),
      len(self.wanted_quantity_matrix.itervalues())
    )

    for order_cell in order_cell_list:
      self.assertEquals(
        order_cell.getQuantity(),
        self.wanted_quantity_matrix[
          order_cell.getProperty('membership_criterion_category')
        ]
      )

  def stepCheckGeneratedDocumentList(self, sequence=None, sequence_list=None,
                          **kw):
    """
    Checks documents generated by Order Builders with its properties
    """
    # XXX: Some values still hardcoded
    organisation = sequence.get('organisation')
    resource = sequence.get('resource')

    generated_document_list = sequence.get('generated_document_list')

    self.assertEquals(
      1, # XXX
      len(generated_document_list)
    )

    order = generated_document_list[0]

    self.assertEquals(
      order.getDestinationValue(),
      organisation
    )

    self.assertEquals(
      order.getStartDate(),
      self.wanted_start_date
    )

    self.assertEquals(
      order.getStopDate(),
      self.wanted_stop_date
    )

    order_line_list = order.contentValues(filter={'portal_type':self.order_line_portal_type})
    self.assertEquals(
      1, # XXX
      len(order_line_list)
    )

    order_line = order_line_list[0] # XXX: add support for more lines and cells too

    self.assertEquals(
      order_line.getResourceValue(),
      resource
    )

    self.assertEquals(
      order_line.getTotalQuantity(),
      self.wanted_quantity
    )

  def stepBuildOrderBuilder(self, sequence=None, sequence_list=None,
                          **kw):
    """
    Invokes build method for Order Builder
    """
    order_builder = sequence.get('order_builder')
    generated_document_list = order_builder.build()
    sequence.edit(generated_document_list = generated_document_list)

  def stepCreateOrderBuilder(self, sequence=None, sequence_list=None,
                          **kw):
    """
    Creates empty Order Builder
    """
    portal_orders = self.portal.portal_orders

    order_builder = portal_orders.newContent(
      portal_type = self.order_builder_portal_type
    )

    sequence.edit(
      order_builder = order_builder
    )

  def stepDecreaseOrganisationResourceQuantityVariated(self, sequence=None, sequence_list=None,
                          **kw):
    """
    Creates movement with variation from organisation to None.
    Using Internal Packing List, confirms it.

    Note: Maybe use InventoryAPITestCase::_makeMovement instead of IPL ?
    """
    organisation = sequence.get('organisation')
    resource = sequence.get('resource')

    packing_list_module = self.portal.getDefaultModule(
      portal_type = self.packing_list_portal_type
    )

    packing_list = packing_list_module.newContent(
      portal_type = self.packing_list_portal_type,
      source_value = organisation,
      start_date = self.datetime
    )

    packing_list_line = packing_list.newContent(
      portal_type = self.packing_list_line_portal_type,
      resource_value = resource,
      quantity = self.decrease_quantity,
    )

    packing_list_line.setVariationCategoryList(
        list(self.decrease_quantity_matrix.iterkeys())
    )

    get_transaction().commit()
    self.tic()

    base_id = 'movement'
    cell_key_list = list(packing_list_line.getCellKeyList(base_id=base_id))
    cell_key_list.sort()

    for cell_key in cell_key_list:
      cell = packing_list_line.newCell(base_id=base_id, \
                                portal_type=self.packing_list_cell_portal_type, *cell_key)
      cell.edit(mapped_value_property_list=['price','quantity'],
                quantity=self.decrease_quantity_matrix[cell_key[0]],
                predicate_category_list=cell_key,
                variation_category_list=cell_key)

    packing_list.confirm()

  def stepDecreaseOrganisationResourceQuantity(self, sequence=None, sequence_list=None,
                          **kw):
    """
    Creates movement from organisation to None.
    Using Internal Packing List, confirms it.

    Note: Maybe use InventoryAPITestCase::_makeMovement instead of IPL ?
    """
    organisation = sequence.get('organisation')
    resource = sequence.get('resource')

    packing_list_module = self.portal.getDefaultModule(
      portal_type = self.packing_list_portal_type
    )

    packing_list = packing_list_module.newContent(
      portal_type = self.packing_list_portal_type,
      source_value = organisation,
      start_date = self.datetime
    )

    packing_list.newContent(
      portal_type = self.packing_list_line_portal_type,
      resource_value = resource,
      quantity = self.decrease_quantity,
    )

    packing_list.confirm()

class TestOrderBuilder(TestOrderBuilderMixin, ERP5TypeTestCase):
  """
    Test Order Builder functionality
  """
  run_all_test = 1

  common_sequence_string = '\
                      ClearActivities \
                      CreateOrganisation \
                      CreateNotVariatedResource \
                      SetMaxDelayOnResource \
                      SetMinFlowOnResource \
                      Tic \
                      DecreaseOrganisationResourceQuantity \
                      Tic \
                      CreateOrderBuilder \
                      FillOrderBuilder \
                      Tic \
                      BuildOrderBuilder \
                      Tic \
                      CheckGeneratedDocumentList \
                      '

  def getTitle(self):
    return "Order Builder"

  def test_01_simpleOrderBuilder(self, quiet=0, run=run_all_test):
    """
    Test simple Order Builder
    """
    if not run: return

    self.wanted_quantity = 1.0
    self.wanted_start_date = self.datetime.earliestTime() \
      + self.order_builder_hardcoded_time_diff

    self.wanted_stop_date = self.datetime.earliestTime() \
      + self.order_builder_hardcoded_time_diff

    sequence_list = SequenceList()
    sequence_list.addSequenceString(self.common_sequence_string)
    sequence_list.play(self)

  def test_01a_simpleOrderBuilderVariatedResource(self, quiet=0, run=run_all_test):
    """
    Test simple Order Builder for Variated Resource
    """
    if not run: return

    sequence_string = '\
                      ClearActivities \
                      CreateOrganisation \
                      CreateVariatedResource \
                      SetMaxDelayOnResource \
                      SetMinFlowOnResource \
                      Tic \
                      DecreaseOrganisationResourceQuantityVariated \
                      Tic \
                      CreateOrderBuilder \
                      FillOrderBuilder \
                      Tic \
                      BuildOrderBuilder \
                      Tic \
                      CheckGeneratedDocumentListVariated \
                      '

    self.wanted_quantity = 1.0
    self.wanted_start_date = self.datetime.earliestTime() \
      + self.order_builder_hardcoded_time_diff

    self.wanted_stop_date = self.datetime.earliestTime() \
      + self.order_builder_hardcoded_time_diff

    self.decrease_quantity_matrix = {
      'size/Man' : 1.0,
      'size/Woman' : 2.0,
    }

    self.wanted_quantity_matrix = self.decrease_quantity_matrix.copy()

    sequence_list = SequenceList()
    sequence_list.addSequenceString(sequence_string)
    sequence_list.play(self)

  def test_02_maxDelayResourceOrderBuilder(self, quiet=0, run=run_all_test):
    """
    Test max_delay impact on generated order start date
    """
    if not run: return

    self.max_delay = 14.0

    self.wanted_quantity = 1.0
    self.wanted_start_date = self.datetime.earliestTime() \
      - self.max_delay \
      + self.order_builder_hardcoded_time_diff

    self.wanted_stop_date = self.datetime.earliestTime() \
      + self.order_builder_hardcoded_time_diff

    sequence_list = SequenceList()
    sequence_list.addSequenceString(self.common_sequence_string)
    sequence_list.play(self)

  def test_03_minFlowResourceOrderBuilder(self, quiet=0, run=run_all_test):
    """
    Test min_flow impact on generated order line quantity
    """
    if not run: return

    self.wanted_quantity = 1.0
    self.wanted_start_date = self.datetime.earliestTime() \
      + self.order_builder_hardcoded_time_diff

    self.wanted_stop_date = self.datetime.earliestTime() \
      + self.order_builder_hardcoded_time_diff

    sequence_list = SequenceList()
    sequence_list.addSequenceString(self.common_sequence_string)

    # case when min_flow > decreased_quantity
    self.min_flow = 144.0
    self.wanted_quantity = self.min_flow + self.decrease_quantity
    # why to order more than needed?
    # self.wanted_quantity = self.min_flow

    sequence_list.play(self)

    # case when min_flow < decreased_quantity
    self.min_flow = 15.0
    self.decrease_quantity = 20.0

    self.wanted_quantity = self.min_flow + self.decrease_quantity
    # why to order more than needed?
    # self.wanted_quantity = self.decreased_quantity

    sequence_list.play(self)

def test_suite():
  suite = unittest.TestSuite()
  suite.addTest(unittest.makeSuite(TestOrderBuilder))
  return suite
