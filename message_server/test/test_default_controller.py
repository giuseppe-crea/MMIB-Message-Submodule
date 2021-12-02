# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound

from message_server.models.draft import Draft  # noqa: E501
from message_server.models.message import Message  # noqa: E501
from message_server.test import BaseTestCase
from message_server.database import Message as DB_Message, db, Blacklist
from message_server.tasks import deliver_message


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_add_blacklist(self):
        """Test case for add_blacklist

        add to user blacklist
        """
        query_string = [('owner', 'owner@example.com'),
                        ('email', 'email@example.com')]
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
        # add a pair, if the pair already exists this still returns 200
        self.test_add_blacklist()
        # check for the pair we just added
        query_string = [('owner', 'owner@example.com'),
                        ('email', 'email@example.com')]
        response = self.client.open(
            '/blacklist',
            method='HEAD',
            content_type='application/json',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        # check for non-existing pair
        query_string = [('owner', 'inexistent@example.com'),
                        ('email', 'email@example.com')]
        response = self.client.open(
            '/blacklist',
            method='HEAD',
            content_type='application/json',
            query_string=query_string)
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_create_draft(self):
        """Test case for create_draft

        create draft
        """
        data = Message()
        # params are assumed to be correct, controlled by gateway
        # trust the network smells but works
        data.message = "this is a test draft"
        data.sender_mail = "sender@example.com"
        data.receiver_mail = "mail1@example.com, mail2@example.com"
        data.time = "2025-01-01 12:00:00"
        data.image = "sample_image.jpg"
        data.image_hash = "small_image_encoded_in_base_64"
        response = self.client.open(
            '/draft',
            method='POST',
            data=json.dumps(data),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        # check the database manually, see if the data is there
        try:
            saved_draft = DB_Message.query.filter_by(
                message=data.message,
                sender_email=data.sender_mail,
                receiver_email=data.receiver_mail
            ).one()
        except NoResultFound or MultipleResultsFound:
            assert False
        # make sure its a real draft
        assert (saved_draft.status == 0)
        # test 400: image_hash is too big
        image_hash_too_big = ''
        for i in range(10241):
            image_hash_too_big += 'a'
        data.image_hash = image_hash_too_big
        response = self.client.open(
            '/draft',
            method='POST',
            data=json.dumps(data),
            content_type='application/json')
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_draft(self):
        """Test case for delete_draft

        delete a draft
        """
        draft_msg = DB_Message.query.filter_by(status=0).first()
        if draft_msg is None:
            self.test_create_draft()
            draft_msg = DB_Message.query.filter_by(status=0).first()
        id = draft_msg.id
        response = self.client.open(
            '/draft/{id}'.format(id=id),
            method='DELETE',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        # now check a random id, the draft shouldn't exist
        id = 18  # chosen by fair dice roll. guaranteed to be random.
        assert (DB_Message.query.filter_by(id=id).first() is None)
        response = self.client.open(
            '/draft/{id}'.format(id=id),
            method='DELETE',
            content_type='application/json')
        # check that the response is still 200 and delete had no effect
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        assert (DB_Message.query.filter_by(id=id).first() is None)

    def test_delete_message(self):
        """Test case for delete_message

        delete a message
        """
        # test for a non-existent id
        query_string = [('email', 'email_example'),
                        ('id', 56)]
        response = self.client.open(
            '/message',
            method='DELETE',
            content_type='application/json',
            query_string=query_string)
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        # create a message
        dummy_msg = DB_Message()
        dummy_msg.add_message(
            "dummy delete message",
            "sender@example.com",
            "receiver@example.com",
            "2025-01-01 12:00:00",
            None,
            None,
            2,
            True
        )
        db.session.add(dummy_msg)
        db.session.commit()
        dummy_id = dummy_msg.get_id()
        # delete the message with an email that's neither sender nor receiver
        query_string = [('email', 'nobody@example.com'),
                        ('id', dummy_id)]
        response = self.client.open(
            '/message',
            method='DELETE',
            content_type='application/json',
            query_string=query_string)
        self.assert400(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        # delete the message for sender
        query_string = [('email', 'sender@example.com'),
                        ('id', dummy_id)]
        response = self.client.open(
            '/message',
            method='DELETE',
            content_type='application/json',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        # check that it's visible to receiver but not sender
        message = DB_Message.query.filter_by(id=dummy_id).first()
        assert message.visible_to_receiver
        assert not message.visible_to_sender
        # delete for receiver too
        query_string = [('email', 'receiver@example.com'),
                        ('id', dummy_id)]
        response = self.client.open(
            '/message',
            method='DELETE',
            content_type='application/json',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        # check that the message is gone
        assert (DB_Message.query.filter_by(id=dummy_id).first() is None)

    def test_edit_draft(self):
        """Test case for edit_draft

        edit a draft
        """
        dummy_msg = DB_Message()
        dummy_msg.add_message(
            "dummy draft to edit",
            "sender@example.com",
            "receiver@example.com",
            "2025-01-01 12:00:00",
            "test_name",
            "test_base64_value",
            0,
            True
        )
        db.session.add(dummy_msg)
        db.session.commit()
        dummy_id = dummy_msg.get_id()
        data = Draft()
        # editing fields
        # the image and image hash fields will be dropped
        data.id = dummy_id
        data.message = "edited draft"
        data.sender_mail = "sender@example.com"
        data.receiver_mail = "receiver@example.com"
        data.time = "2025-01-01 12:00:00"
        response = self.client.open(
            '/draft',
            method='PUT',
            data=json.dumps(data),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        # check that the message was actually edited
        assert DB_Message.query.filter_by(
            id=dummy_id
        ).first().message == data.message

    def test_get_blacklist(self):
        """Test case for get_blacklist

        get the user's blacklist
        """
        response = self.client.open(
            '/blacklist/{owner}'.format(owner='owner_example'),
            method='GET',
            content_type='application/json')
        self.assert404(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        new_blacklist_element = Blacklist()
        new_blacklist_element.add_blocked_user("owner_example", "blocked_ex")
        db.session.add(new_blacklist_element)
        db.session.commit()
        # test getting an element
        response = self.client.open(
            '/blacklist/{owner}'.format(owner='owner_example'),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        assert b'blocked_ex' in response.data
        # clean up after myself
        db.session.delete(new_blacklist_element)
        db.session.commit()

    def test_get_drafts(self):
        """Test case for get_drafts

        get the user's drafts list
        """
        # create a message
        dummy_msg = DB_Message()
        dummy_msg.add_message(
            "dummy get drafts message",
            "sender@example.com",
            "receiver@example.com",
            "2025-01-01 12:00:00",
            None,
            None,
            0,
            True
        )
        db.session.add(dummy_msg)
        db.session.commit()
        response = self.client.open(
            '/drafts/{owner}'.format(owner='sender@example.com'),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        assert b'dummy get drafts message' in response.data
        # cleanup
        db.session.delete(dummy_msg)
        db.session.commit()

    def test_get_inbox(self):
        """Test case for get_inbox

        get the user's inbox
        """
        # create a message with status 1 and one with status 2
        dummy_msg_1 = DB_Message()
        dummy_msg_1.add_message(
            "dummy invisible message",
            "sender@example.com",
            "receiver@example.com",
            "2025-01-01 12:00:00",
            None,
            None,
            1,
            True
        )
        dummy_msg_2 = DB_Message()
        dummy_msg_2.add_message(
            "dummy visible message",
            "sender@example.com",
            "receiver@example.com",
            "2025-01-01 12:00:00",
            None,
            None,
            2,
            True
        )
        db.session.add(dummy_msg_1)
        db.session.add(dummy_msg_2)
        db.session.commit()
        response = self.client.open(
            '/inbox/{owner}'.format(owner='receiver@example.com'),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        assert b'dummy visible message' in response.data
        assert b'dummy invisible message' not in response.data
        # cleanup
        db.session.delete(dummy_msg_1)
        db.session.delete(dummy_msg_2)
        db.session.commit()

    def test_get_outbox(self):
        """Test case for get_outbox

        get the user's outbox
        """
        # create a message with status 1 and one with status 2
        dummy_msg_1 = DB_Message()
        dummy_msg_1.add_message(
            "dummy pending message",
            "sender@example.com",
            "receiver@example.com",
            "2025-01-01 12:00:00",
            None,
            None,
            1,
            True
        )
        dummy_msg_2 = DB_Message()
        dummy_msg_2.add_message(
            "dummy sent message",
            "sender@example.com",
            "receiver@example.com",
            "2025-01-01 12:00:00",
            None,
            None,
            2,
            True
        )
        db.session.add(dummy_msg_1)
        db.session.add(dummy_msg_2)
        db.session.commit()
        response = self.client.open(
            '/outbox/{owner}'.format(owner='sender@example.com'),
            method='GET',
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        assert b'dummy pending message' in response.data
        assert b'dummy sent message' in response.data
        # cleanup
        db.session.delete(dummy_msg_1)
        db.session.delete(dummy_msg_2)
        db.session.commit()

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
        # params are assumed to be correct, controlled by gateway
        # trust the network smells but works
        data.message = "this is a test message"
        data.sender_mail = "sender@example.com"
        data.receiver_mail = "mail1@example.com, mail2@example.com"
        data.time = "2025-01-01 12:00:00"
        data.image = "sample_image.jpg"
        data.image_hash = "small_image_encoded_in_base_64"
        response = self.client.open(
            '/message',
            method='POST',
            data=json.dumps(data),
            content_type='application/json')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))
        sent_ids = response.json
        # check that messages were added to the database
        for id in sent_ids:
            try:
                query_msg = DB_Message.query.filter_by(id=id).one()
            except NoResultFound or MultipleResultsFound:
                assert False
            # check that message is pending
            assert query_msg.status == 1
            # force deliver message
            deliver_message(id)
            # query the message again
            query_msg = DB_Message.query.filter_by(id=id).one()
            # assert it's been delivered
            assert query_msg.status == 2

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
