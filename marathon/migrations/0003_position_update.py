# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Finisher', fields ['race', 'bib_number']
        db.delete_unique(u'marathon_finisher', ['race_id', 'bib_number'])

        # Deleting model 'Finisher'
        db.delete_table(u'marathon_finisher')

        # Deleting model 'RaceType'
        db.delete_table(u'marathon_racetype')

        # Deleting model 'Race'
        db.delete_table(u'marathon_race')

        # Deleting model 'TextTag'
        db.delete_table(u'marathon_texttag')

        # Adding model 'PositionUpdate'
        db.create_table(u'marathon_positionupdate', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('spectator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='positionupdates', to=orm['marathon.Spectator'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now, db_index=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')(db_index=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')(db_index=True)),
            ('accuracy', self.gf('django.db.models.fields.FloatField')(db_index=True)),
        ))
        db.send_create_signal(u'marathon', ['PositionUpdate'])

        # Deleting field 'RunnerTag.distance'
        db.delete_column(u'marathon_runnertag', 'distance')

        # Deleting field 'RunnerTag.finisher'
        db.delete_column(u'marathon_runnertag', 'finisher_id')

        # Adding field 'RunnerTag.accuracy'
        db.add_column(u'marathon_runnertag', 'accuracy',
                      self.gf('django.db.models.fields.FloatField')(default=0, db_index=True),
                      keep_default=False)

        # Adding index on 'RunnerTag', fields ['longitude']
        db.create_index(u'marathon_runnertag', ['longitude'])

        # Adding index on 'RunnerTag', fields ['latitude']
        db.create_index(u'marathon_runnertag', ['latitude'])

        # Deleting field 'Video.distance'
        db.delete_column(u'marathon_video', 'distance')

        # Deleting field 'Video.longitude'
        db.delete_column(u'marathon_video', 'longitude')

        # Deleting field 'Video.latitude'
        db.delete_column(u'marathon_video', 'latitude')

        # Adding field 'Video.online'
        db.add_column(u'marathon_video', 'online',
                      self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True),
                      keep_default=False)

        # Adding field 'Video.public'
        db.add_column(u'marathon_video', 'public',
                      self.gf('django.db.models.fields.BooleanField')(default=False, db_index=True),
                      keep_default=False)


    def backwards(self, orm):
        # Removing index on 'RunnerTag', fields ['latitude']
        db.delete_index(u'marathon_runnertag', ['latitude'])

        # Removing index on 'RunnerTag', fields ['longitude']
        db.delete_index(u'marathon_runnertag', ['longitude'])

        # Adding model 'Finisher'
        db.create_table(u'marathon_finisher', (
            ('race', self.gf('django.db.models.fields.related.ForeignKey')(related_name='runners', to=orm['marathon.Race'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('finish_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('bib_number', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'marathon', ['Finisher'])

        # Adding unique constraint on 'Finisher', fields ['race', 'bib_number']
        db.create_unique(u'marathon_finisher', ['race_id', 'bib_number'])

        # Adding model 'RaceType'
        db.create_table(u'marathon_racetype', (
            ('distance', self.gf('django.db.models.fields.FloatField')(db_index=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
        ))
        db.send_create_signal(u'marathon', ['RaceType'])

        # Adding model 'Race'
        db.create_table(u'marathon_race', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('racetype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['marathon.RaceType'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='races', to=orm['marathon.Event'])),
        ))
        db.send_create_signal(u'marathon', ['Race'])

        # Adding model 'TextTag'
        db.create_table(u'marathon_texttag', (
            ('text', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(related_name='texttags', to=orm['marathon.Video'])),
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'marathon', ['TextTag'])

        # Deleting model 'PositionUpdate'
        db.delete_table(u'marathon_positionupdate')

        # Adding field 'RunnerTag.distance'
        db.add_column(u'marathon_runnertag', 'distance',
                      self.gf('django.db.models.fields.FloatField')(default=0, db_index=True),
                      keep_default=False)

        # Adding field 'RunnerTag.finisher'
        db.add_column(u'marathon_runnertag', 'finisher',
                      self.gf('django.db.models.fields.related.ForeignKey')(related_name='tags', null=True, to=orm['marathon.Finisher']),
                      keep_default=False)

        # Deleting field 'RunnerTag.accuracy'
        db.delete_column(u'marathon_runnertag', 'accuracy')

        # Adding field 'Video.distance'
        db.add_column(u'marathon_video', 'distance',
                      self.gf('django.db.models.fields.FloatField')(default=0, db_index=True),
                      keep_default=False)

        # Adding field 'Video.longitude'
        db.add_column(u'marathon_video', 'longitude',
                      self.gf('django.db.models.fields.FloatField')(default=-1.13),
                      keep_default=False)

        # Adding field 'Video.latitude'
        db.add_column(u'marathon_video', 'latitude',
                      self.gf('django.db.models.fields.FloatField')(default=52.95),
                      keep_default=False)

        # Deleting field 'Video.online'
        db.delete_column(u'marathon_video', 'online')

        # Deleting field 'Video.public'
        db.delete_column(u'marathon_video', 'public')


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
        u'marathon.event': {
            'Meta': {'object_name': 'Event'},
            'date': ('django.db.models.fields.DateField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'})
        },
        u'marathon.positionupdate': {
            'Meta': {'object_name': 'PositionUpdate'},
            'accuracy': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'spectator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'positionupdates'", 'to': u"orm['marathon.Spectator']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'})
        },
        u'marathon.runnertag': {
            'Meta': {'object_name': 'RunnerTag'},
            'accuracy': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'runner_number': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'runnertags'", 'to': u"orm['marathon.Video']"})
        },
        u'marathon.spectator': {
            'Meta': {'object_name': 'Spectator'},
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True'})
        },
        u'marathon.video': {
            'Meta': {'object_name': 'Video'},
            'duration': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'videos'", 'to': u"orm['marathon.Event']"}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'online': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'public': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'spectator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'videos'", 'to': u"orm['marathon.Spectator']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'db_index': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['marathon']