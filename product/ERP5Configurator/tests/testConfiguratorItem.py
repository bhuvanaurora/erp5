##############################################################################
# Copyright (c) 2012 Nexedi SA and Contributors. All Rights Reserved.
#                     Rafael Monnerat <rafael@nexedi.com>
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
##############################################################################


from AccessControl import Unauthorized
import uuid
from Products.ERP5Configurator.tests.ConfiguratorTestMixin import \
                                             TestLiveConfiguratorWorkflowMixin

from Products.ERP5Configurator import tests as test_folder

class TestConfiguratorItem(TestLiveConfiguratorWorkflowMixin):
  """
    Test the Configurator Tool
  """

  def getBusinessTemplateList(self):
    return ('erp5_core_proxy_field_legacy',
            'erp5_full_text_myisam_catalog',
            'erp5_base',
            'erp5_workflow',
            'erp5_configurator')

  def createConfigurationSave(self):
    """ Create a Business Configuration and a Configuration Save 
    """
    bc = self.portal.business_configuration_module.newContent()
    return bc.newContent(portal_type="Configuration Save")
    

  def newUniqueUID(self):
    """ Return a unique number id"""
    return str(uuid.uuid1())

  def testOrganisationConfiguratorItem(self):
    """
      The Anonymous user can not have access to view the Configurator Tool.
    """
    configuration_save = self.createConfigurationSave()

    group_id = "some_group"

    title = "test_%s" % self.newUniqueUID()
    kw = { 'title': title,
           'corporate_name': "test_corporate_name",
           'default_address_city': 'test_default_address_city',
           'default_email_text': 'test_default_email_text',
           'default_telephone_text': 'test_default_telephone_text',
           'default_address_zip_code': 'test_default_address_zip_code',
           'default_address_region': 'test_default_address_region',
           'default_address_street_address': 'test_default_address_street_address',
         }


    item = configuration_save.addConfigurationItem(  
      "Organisation Configurator Item",
      group=group_id, site='main', **kw)

    self.stepTic()
    item._build(configuration_save.getParentValue())
    self.stepTic()

    organisation = self.portal.portal_catalog.getResultValue(
                       portal_type="Organisation", 
                       title = title)

    self.assertNotEquals(organisation, None)
    
    self.assertEquals(group_id, organisation.getGroup())
    self.assertEquals(kw['title'], organisation.getTitle())
    self.assertEquals(kw['corporate_name'], organisation.getCorporateName())
    self.assertEquals(kw['default_address_city'],
                      organisation.getDefaultAddressCity())
    self.assertEquals(kw['default_email_text'],
                      organisation.getDefaultEmailText())
    self.assertEquals(kw['default_telephone_text'],
                      organisation.getDefaultTelephoneText())
    self.assertEquals(kw['default_address_zip_code'],
                      organisation.getDefaultAddressZipCode())
    self.assertEquals(kw['default_address_region'],
                      organisation.getDefaultAddressRegion())

    self.assertEquals(kw['default_address_street_address'],
                      organisation.getDefaultAddressStreetAddress())

    self.assertEquals('main', organisation.getSite())
    self.assertEquals('validated', organisation.getValidationState())


  def testCategoryConfiguratorItem(self):
    """ Test Category Configurator Item """
    configuration_save = self.createConfigurationSave()
    bc = configuration_save.getParentValue()
    
    category_id_0 = "test_category_%s" % self.newUniqueUID()
    item0 = configuration_save.addConfigurationItem(
                                        "Category Configurator Item",
                                        category_root='group',
                                        object_id=category_id_0,
                                        title="title_%s" % category_id_0)

    category_id_1 = "test_category_%s" % self.newUniqueUID()
    item1 = configuration_save.addConfigurationItem(
                                        "Category Configurator Item",
                                        category_root='group',
                                        object_id=category_id_1,
                                        title="title_%s" % category_id_1)

    self.stepTic()
    item0._build(bc)
    self.stepTic()

    category_0 = getattr(self.portal.portal_categories.group, category_id_0, None)
    self.assertNotEquals(category_0, None)
    self.assertEquals(category_0.getTitle(), "title_%s" % category_id_0)

    category_1 = getattr(self.portal.portal_categories.group, category_id_1, None)
    self.assertEquals(category_1, None)

    item1._build(bc)
    self.stepTic()

    category_1 = getattr(self.portal.portal_categories.group, category_id_1, None)
    self.assertNotEquals(category_1, None)
    self.assertEquals(category_1.getTitle(), "title_%s" % category_id_1)

    # recreate category_1 with new title

    item2 = configuration_save.addConfigurationItem(
                                        "Category Configurator Item",
                                        category_root='group',
                                        object_id=category_id_1,
                                        title="new_title_%s" % category_id_1)

    item2._build(bc)
    self.stepTic()

    category_1 = getattr(self.portal.portal_categories.group, 
                         category_id_1, None)
    self.assertNotEquals(category_1, None)
    self.assertEquals(category_1.getTitle(), "new_title_%s" % category_id_1)

  def testCurrencyConfiguratorItem(self):
    """ Test Category Configurator Item """
    configuration_save = self.createConfigurationSave()
    bc = configuration_save.getParentValue()

    eur_currency_id = "EUR"
    eur_currency_title = "Euro"
    item_eur = configuration_save.addConfigurationItem(
                             "Currency Configurator Item",
                             reference = eur_currency_id,
                             base_unit_quantity = 0.01,
                             title = eur_currency_title,)

    brl_currency_id = "BRL"
    brl_currency_title = "Brazillian Real"
    item_brl = configuration_save.addConfigurationItem(
                             "Currency Configurator Item",
                             reference = brl_currency_id,
                             base_unit_quantity = 0.01,
                             title = brl_currency_title,)

    self.stepTic()

    item_eur._build(bc)
    self.stepTic()

    eur = getattr(self.portal.currency_module, eur_currency_id , None)
    self.assertNotEquals(eur, None)
    self.assertEquals(eur.getTitle(), eur_currency_title)

    brl = getattr(self.portal.currency_module, brl_currency_id , None)
    self.assertEquals(brl, None)

    item_brl._build(bc)
    self.stepTic()

    brl = getattr(self.portal.currency_module, brl_currency_id , None)
    self.assertNotEquals(brl, None)
    self.assertEquals(brl.getTitle(), brl_currency_title)

    # Build several times to not break portal.

    item_brl._build(bc)
    self.stepTic()
    item_brl._build(bc)
    self.stepTic()

  def testPortalTypeRolesSpreadsheetConfiguratorItem(self):
    """ Test Portal Type Roles Configurator Item """
    configuration_save = self.createConfigurationSave()
    bc = configuration_save.getParentValue()
    category_tool = self.portal.portal_categories

    test_folder_path = '/'.join(test_folder.__file__.split('/')[:-1])

    f = open("%s/test_data/test_standard_portal_type_roles.ods" \
               % test_folder_path, "r")
    try:
      data = f.read()
    finally:
      f.close()

    if getattr(category_tool.group, "my_group", None) is None:
      category_tool.group.newContent(id="my_group")

    item = configuration_save.addConfigurationItem(
      "Portal Type Roles Spreadsheet Configurator Item",
      configuration_spreadsheet_data = data)


    person_type = self.portal.portal_types["Person"]
    person_module_type = self.portal.portal_types["Person Module"]

    role_list = [i for i in person_type.objectValues(
                 portal_type="Role Information")
                 if i.getTitle() == "TestRole_Person"]

    if len(role_list) > 0:
      person_type.manage_delObjects([i.id for i in role_list])

    role_list = [i for i in person_module_type.objectValues(
                 portal_type="Role Information")
                if i.getTitle() == "TestRole_PersonModule"]

    if len(role_list) > 0:
      person_module_type.manage_delObjects([i.id for i in role_list])

    self.stepTic()
    item._build(bc)
    self.stepTic()

    role_list = [i for i in person_type.objectValues(
                 portal_type="Role Information") 
                if i.getTitle() == "TestRole_Person"]

    self.assertEquals(len(role_list), 1)

    self.assertEquals(role_list[0].getDescription(), 
                      "Configured by ERP5 Configurator")

    self.assertEquals(role_list[0].getRoleNameList(), 
                      ['Auditor', 'Author', 'Assignee'])

    self.assertEquals(role_list[0].getRoleCategoryList(),
                      ['group/my_group',])


    role_list = [i for i in person_module_type.objectValues(
                 portal_type="Role Information")
                if i.getTitle() == "TestRole_PersonModule"]

    self.assertEquals(len(role_list), 1)

    self.assertEquals(role_list[0].getDescription(),
                      "Configured by ERP5 Configurator")

    self.assertEquals(role_list[0].getRoleNameList(),
                      ['Auditor', 'Author'])

    self.assertEquals(role_list[0].getRoleCategoryList(),
                      ['group/my_group',])


  def testCategoriesSpreadsheetConfiguratorItem(self):
    """ Test Portal Type Roles Configurator Item """
    configuration_save = self.createConfigurationSave()
    bc = configuration_save.getParentValue()
    category_tool = self.portal.portal_categories

    test_folder_path = '/'.join(test_folder.__file__.split('/')[:-1])

    f = open("%s/test_data/test_standard_categories.ods" \
               % test_folder_path, "r")
    try:
      data = f.read()
    finally:
      f.close()

    item = configuration_save.addConfigurationItem(
      "Categories Spreadsheet Configurator Item",
      configuration_spreadsheet_data = data)

    self.stepTic()
    item._build(bc)
    self.stepTic()

    base_category_list = ["group", "site", "business_application", 
                          "function", "region"]

    for base_category_id in base_category_list:
      # Check first Level
      base_category = getattr(category_tool, base_category_id)    
      my_test = getattr(base_category, "my_test", None)
      self.assertNotEquals(my_test, None)
      self.assertEquals(my_test.getTitle(), "TEST")
      self.assertEquals(my_test.getDescription(), "TEST")
      self.assertEquals(my_test.getCodification(), "TEST")
      self.assertEquals(my_test.getIntIndex(), 1)
      # Check Second level
      my_test = getattr(my_test, "my_test", None)
      self.assertNotEquals(my_test, None)
      self.assertEquals(my_test.getTitle(), "TEST")
      self.assertEquals(my_test.getDescription(), "TEST")
      self.assertEquals(my_test.getCodification(), "TEST")
      self.assertEquals(my_test.getIntIndex(), 2)

      # Check Thrid level
      my_test = getattr(my_test, "my_test", None)
      self.assertNotEquals(my_test, None)
      self.assertEquals(my_test.getTitle(), "TEST")
      self.assertEquals(my_test.getDescription(), "TEST")
      self.assertEquals(my_test.getCodification(), "TEST")
      self.assertEquals(my_test.getIntIndex(), 3)











