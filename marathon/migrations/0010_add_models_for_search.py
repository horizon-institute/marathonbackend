# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LocationName'
        db.create_table(u'marathon_locationname', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='Unknown', max_length=50, db_index=True)),
        ))
        db.send_create_signal(u'marathon', ['LocationName'])

        # Adding model 'VideoDistance'
        db.create_table(u'marathon_videodistance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reference_point', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['marathon.RacePoint'])),
            ('accuracy', self.gf('django.db.models.fields.FloatField')(db_index=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['marathon.Video'])),
        ))
        db.send_create_signal(u'marathon', ['VideoDistance'])

        # Adding model 'LocationDistance'
        db.create_table(u'marathon_locationdistance', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('reference_point', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['marathon.RacePoint'])),
            ('accuracy', self.gf('django.db.models.fields.FloatField')(db_index=True)),
            ('location_name', self.gf('django.db.models.fields.related.ForeignKey')(related_name='points', to=orm['marathon.LocationName'])),
        ))
        db.send_create_signal(u'marathon', ['LocationDistance'])

        # Adding model 'RaceResult'
        db.create_table(u'marathon_raceresult', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['marathon.Event'])),
            ('runner_number', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(db_index=True, max_length=200, null=True, blank=True)),
            ('finishing_time', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('club', self.gf('django.db.models.fields.related.ForeignKey')(related_name='runners', null=True, to=orm['marathon.RunningClub'])),
        ))
        db.send_create_signal(u'marathon', ['RaceResult'])

        # Adding model 'RacePoint'
        db.create_table(u'marathon_racepoint', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['marathon.Event'])),
            ('latitude', self.gf('django.db.models.fields.FloatField')(db_index=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(db_index=True)),
            ('distance', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
        ))
        db.send_create_signal(u'marathon', ['RacePoint'])

        # Adding model 'RunningClub'
        db.create_table(u'marathon_runningclub', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
        ))
        db.send_create_signal(u'marathon', ['RunningClub'])

        # Adding index on 'ContentFlag', fields ['content_type']
        db.create_index(u'marathon_contentflag', ['content_type'])


    def backwards(self, orm):
        # Removing index on 'ContentFlag', fields ['content_type']
        db.delete_index(u'marathon_contentflag', ['content_type'])

        # Deleting model 'LocationName'
        db.delete_table(u'marathon_locationname')

        # Deleting model 'VideoDistance'
        db.delete_table(u'marathon_videodistance')

        # Deleting model 'LocationDistance'
        db.delete_table(u'marathon_locationdistance')

        # Deleting model 'RaceResult'
        db.delete_table(u'marathon_raceresult')

        # Deleting model 'RacePoint'
        db.delete_table(u'marathon_racepoint')

        # Deleting model 'RunningClub'
        db.delete_table(u'marathon_runningclub')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Group']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "u'user_set'", 'blank': 'True', 'to': u"orm['auth.Permission']"}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'marathon.contactregistration': {
            'Meta': {'object_name': 'ContactRegistration'},
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'registration_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'})
        },
        u'marathon.contentflag': {
            'Meta': {'object_name': 'ContentFlag'},
            'content_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'content_type': ('django.db.models.fields.CharField', [], {'max_length': '15', 'db_index': 'True'}),
            'flag_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reason': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']", 'null': 'True', 'blank': 'True'})
        },
        u'marathon.event': {
            'Meta': {'object_name': 'Event'},
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_current': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        },
        u'marathon.locationdistance': {
            'Meta': {'object_name': 'LocationDistance'},
            'accuracy': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location_name': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'points'", 'to': u"orm['marathon.LocationName']"}),
            'reference_point': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['marathon.RacePoint']"})
        },
        u'marathon.locationname': {
            'Meta': {'object_name': 'LocationName'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'Unknown'", 'max_length': '50', 'db_index': 'True'})
        },
        u'marathon.positionupdate': {
            'Meta': {'object_name': 'PositionUpdate'},
            'accuracy': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'server_created_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'server_updated_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'spectator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'positionupdates'", 'to': u"orm['marathon.Spectator']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'})
        },
        u'marathon.racepoint': {
            'Meta': {'object_name': 'RacePoint'},
            'distance': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['marathon.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'})
        },
        u'marathon.raceresult': {
            'Meta': {'object_name': 'RaceResult'},
            'club': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'runners'", 'null': 'True', 'to': u"orm['marathon.RunningClub']"}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['marathon.Event']"}),
            'finishing_time': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '200', 'null': 'True', 'blank': 'True'}),
            'runner_number': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'})
        },
        u'marathon.runnertag': {
            'Meta': {'object_name': 'RunnerTag'},
            'accuracy': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'runner_number': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'server_created_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'server_updated_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'thumbnail': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'runnertags'", 'to': u"orm['marathon.Video']"})
        },
        u'marathon.runningclub': {
            'Meta': {'object_name': 'RunningClub'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        u'marathon.spectator': {
            'Meta': {'object_name': 'Spectator'},
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'server_created_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'server_updated_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True'})
        },
        u'marathon.video': {
            'Meta': {'object_name': 'Video'},
            'duration': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'videos'", 'to': u"orm['marathon.Event']"}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'online': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'server_created_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'server_last_modified': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'server_updated_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'spectator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'videos'", 'to': u"orm['marathon.Spectator']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'thumbnail': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300'}),
            'url': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '300', 'db_index': 'True'})
        },
        u'marathon.videodistance': {
            'Meta': {'object_name': 'VideoDistance'},
            'accuracy': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'reference_point': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['marathon.RacePoint']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['marathon.Video']"})
        }
    }

    complete_apps = ['marathon']