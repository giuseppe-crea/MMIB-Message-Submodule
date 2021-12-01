# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from message_server.models.draft import Draft  # noqa: E501
from message_server.models.message import Message  # noqa: E501
from message_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_add_blacklist(self):
        """Test case for add_blacklist

        add to user blacklist
        """
        query_string = [('owner', 'owner_example'),
                        ('email', 'email_example')]
        response = self.client.open(
            '/blacklist',
            method='PUT',
            content_type='application/json',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_check_blacklist(self):
        """Test case for check_blacklist

        check the user blacklist
        """
        data = 'data_example'
        response = self.client.open(
            '/blacklist',
            method='HEAD',
            data=json.dumps(data),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_create_draft(self):
        """Test case for create_draft

        create draft
        """
        data = Message()
        response = self.client.open(
            '/draft',
            method='POST',
            data=json.dumps(data),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_draft(self):
        """Test case for delete_draft

        delete a draft
        """
        response = self.client.open(
            '/draft/{id}'.format(id=56),
            method='DELETE',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_message(self):
        """Test case for delete_message

        delete a message
        """
        query_string = [('email', 'email_example'),
                        ('id', 56)]
        response = self.client.open(
            '/message',
            method='DELETE',
            content_type='application/json',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_edit_draft(self):
        """Test case for edit_draft

        edit a draft
        """
        data = Draft()
        response = self.client.open(
            '/draft',
            method='PUT',
            data=json.dumps(data),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_blacklist(self):
        """Test case for get_blacklist

        get the user's blacklist
        """
        response = self.client.open(
            '/blacklist/{owner}'.format(owner='owner_example'),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_drafts(self):
        """Test case for get_drafts

        get the user's drafts list
        """
        response = self.client.open(
            '/drafts/{owner}'.format(owner='owner_example'),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_inbox(self):
        """Test case for get_inbox

        get the user's inbox
        """
        response = self.client.open(
            '/inbox/{owner}'.format(owner='owner_example'),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_outbox(self):
        """Test case for get_outbox

        get the user's outbox
        """
        response = self.client.open(
            '/outbox/{owner}'.format(owner='owner_example'),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_remove_blacklist(self):
        """Test case for remove_blacklist

        remove from user blacklist
        """
        query_string = [('owner', 'owner_example'),
                        ('email', 'email_example')]
        response = self.client.open(
            '/blacklist',
            method='DELETE',
            content_type='application/json',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_send_message(self):
        """Test case for send_message

        send a message
        """
        data = Message()
        response = self.client.open(
            '/message',
            method='POST',
            data=json.dumps(data),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_set_as_read(self):
        """Test case for set_as_read

        set as read
        """
        response = self.client.open(
            '/message/{id}'.format(id='id_example'),
            method='PUT',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_withdraw(self):
        """Test case for withdraw

        withdraw a message
        """
        response = self.client.open(
            '/withdraw/{id}'.format(id='id_example'),
            method='DELETE',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
