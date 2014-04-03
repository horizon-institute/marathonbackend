# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Finisher'
        db.create_table(u'marathon_finisher', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('race', self.gf('django.db.models.fields.related.ForeignKey')(related_name='runners', to=orm['marathon.Race'])),
            ('bib_number', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('finish_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
        ))
        db.send_create_signal(u'marathon', ['Finisher'])

        # Adding unique constraint on 'Finisher', fields ['race', 'bib_number']
        db.create_unique(u'marathon_finisher', ['race_id', 'bib_number'])

        # Adding model 'RaceType'
        db.create_table(u'marathon_racetype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('distance', self.gf('django.db.models.fields.FloatField')(db_index=True)),
        ))
        db.send_create_signal(u'marathon', ['RaceType'])

        # Adding model 'RunnerTag'
        db.create_table(u'marathon_runnertag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(related_name='runnertags', to=orm['marathon.Video'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('distance', self.gf('django.db.models.fields.FloatField')(db_index=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('runner_number', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('finisher', self.gf('django.db.models.fields.related.ForeignKey')(related_name='tags', null=True, to=orm['marathon.Finisher'])),
        ))
        db.send_create_signal(u'marathon', ['RunnerTag'])

        # Adding model 'Video'
        db.create_table(u'marathon_video', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='videos', to=orm['marathon.Event'])),
            ('spectator', self.gf('django.db.models.fields.related.ForeignKey')(related_name='videos', to=orm['marathon.Spectator'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
            ('duration', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('distance', self.gf('django.db.models.fields.FloatField')(db_index=True)),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=300)),
        ))
        db.send_create_signal(u'marathon', ['Video'])

        # Adding model 'Spectator'
        db.create_table(u'marathon_spectator', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('guid', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, null=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
        ))
        db.send_create_signal(u'marathon', ['Spectator'])

        # Adding model 'Race'
        db.create_table(u'marathon_race', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
            ('event', self.gf('django.db.models.fields.related.ForeignKey')(related_name='races', to=orm['marathon.Event'])),
            ('racetype', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['marathon.RaceType'])),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')(db_index=True)),
        ))
        db.send_create_signal(u'marathon', ['Race'])

        # Adding model 'Event'
        db.create_table(u'marathon_event', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('date', self.gf('django.db.models.fields.DateField')(db_index=True)),
            ('public', self.gf('django.db.models.fields.BooleanField')(db_index=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200, db_index=True)),
        ))
        db.send_create_signal(u'marathon', ['Event'])

        # Adding model 'TextTag'
        db.create_table(u'marathon_texttag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('video', self.gf('django.db.models.fields.related.ForeignKey')(related_name='texttags', to=orm['marathon.Video'])),
        ))
        db.send_create_signal(u'marathon', ['TextTag'])


    def backwards(self, orm):
        # Removing unique constraint on 'Finisher', fields ['race', 'bib_number']
        db.delete_unique(u'marathon_finisher', ['race_id', 'bib_number'])

        # Deleting model 'Finisher'
        db.delete_table(u'marathon_finisher')

        # Deleting model 'RaceType'
        db.delete_table(u'marathon_racetype')

        # Deleting model 'RunnerTag'
        db.delete_table(u'marathon_runnertag')

        # Deleting model 'Video'
        db.delete_table(u'marathon_video')

        # Deleting model 'Spectator'
        db.delete_table(u'marathon_spectator')

        # Deleting model 'Race'
        db.delete_table(u'marathon_race')

        # Deleting model 'Event'
        db.delete_table(u'marathon_event')

        # Deleting model 'TextTag'
        db.delete_table(u'marathon_texttag')


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
            'public': ('django.db.models.fields.BooleanField', [], {'db_index': 'True'})
        },
        u'marathon.finisher': {
            'Meta': {'unique_together': "(('race', 'bib_number'),)", 'object_name': 'Finisher'},
            'bib_number': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'finish_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'race': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'runners'", 'to': u"orm['marathon.Race']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        u'marathon.race': {
            'Meta': {'object_name': 'Race'},
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'races'", 'to': u"orm['marathon.Event']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'racetype': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['marathon.RaceType']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'})
        },
        u'marathon.racetype': {
            'Meta': {'object_name': 'RaceType'},
            'distance': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'})
        },
        u'marathon.runnertag': {
            'Meta': {'object_name': 'RunnerTag'},
            'distance': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'finisher': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tags'", 'null': 'True', 'to': u"orm['marathon.Finisher']"}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'runner_number': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'runnertags'", 'to': u"orm['marathon.Video']"})
        },
        u'marathon.spectator': {
            'Meta': {'object_name': 'Spectator'},
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200', 'db_index': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['auth.User']", 'unique': 'True', 'null': 'True'})
        },
        u'marathon.texttag': {
            'Meta': {'object_name': 'TextTag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'texttags'", 'to': u"orm['marathon.Video']"})
        },
        u'marathon.video': {
            'Meta': {'object_name': 'Video'},
            'distance': ('django.db.models.fields.FloatField', [], {'db_index': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'event': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'videos'", 'to': u"orm['marathon.Event']"}),
            'guid': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'spectator': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'videos'", 'to': u"orm['marathon.Spectator']"}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {'db_index': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '300'})
        }
    }

    complete_apps = ['marathon']