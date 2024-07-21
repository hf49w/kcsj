from django.db import models

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name




class Video(models.Model):
    #url	标题	简介	播放量	弹幕	评论数	点赞	投币	收藏	分享	标签
    url = models.URLField('url',max_length=200,primary_key=True)  
    title = models.CharField('标题',max_length=200)
    intro = models.CharField('简介',max_length=500)
    browse = models.IntegerField('播放量')
    danmu = models.IntegerField('弹幕')
    num_comments = models.IntegerField('评论数')
    num_likes = models.IntegerField('点赞')
    num_coins = models.IntegerField('投币')
    num_collect = models.IntegerField('收藏')
    num_share = models.IntegerField('分享')
    tags = models.ManyToManyField(Tag, related_name='videos')
    v_class = models.CharField("分区",max_length=20,default=' ')
    v_detailed_class = models.CharField("细分分区",max_length=20,default=' ')
    v_split = models.CharField("分词",max_length=1000,default=' ')

    comments1 = models.CharField(max_length=1000,default=' ')
    comments2 = models.CharField(max_length=1000,default=' ')
    comments3 = models.CharField(max_length=1000,default=' ')
    comments4 = models.CharField(max_length=1000,default=' ')
    comments5 = models.CharField(max_length=1000,default=' ')


    class Meta:
        db_table ='video'
        verbose_name='视频'
        verbose_name_plural = verbose_name
        managed = True
    def __str__(self):
        return '%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s|%s'%(self.url,self.title,self.intro,self.browse,self.danmu,
                                                      self.num_comments,self.num_likes,self.num_coins,
                                                      self.num_collect,self.num_share,self.tags,self.comments
                                                      )    
    