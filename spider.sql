CREATE TABLE `scrapy-spider`.`jobbole_article` (
  `url_object_id` VARCHAR(50) NOT NULL,
  `title` VARCHAR(200) NOT NULL,
  `url` VARCHAR(300) NOT NULL,
  `front_image_url` VARCHAR(300) NULL,
  `front_image_path` VARCHAR(200) NULL,
  `praise_nums` INT(11) NOT NULL DEFAULT 0,
  `comment_nums` INT(11) NOT NULL DEFAULT 0,
  `fav_nums` INT(11) NULL DEFAULT 0,
  `tags` VARCHAR(200) NULL,
  `content` LONGTEXT NOT NULL,
  `create_date` DATETIME NULL,
  PRIMARY KEY (`url_object_id`));

CREATE TABLE `scrapy-spider`.`zhihu_question` (
  `zhihu_id` bigint(20) NOT NULL DEFAULT '0',
  `topics` varchar(255) DEFAULT NULL,
  `url` varchar(300) NOT NULL,
  `title` varchar(300) NOT NULL,
  `content` longtext NOT NULL,
  `answer_num` int(11) NOT NULL,
  `comments_num` int(11) NOT NULL,
  `watch_user_num` int(11) NOT NULL,
  `click_num` int(11) NOT NULL,
  `create_time` datetime DEFAULT NULL,
  `update_time` datetime DEFAULT NULL,
  `crawl_time` datetime NOT NULL,
  `crawl_update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`zhihu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `scrapy-spider`.`zhihu_answer` (
  `zhihu_id` bigint(20) NOT NULL DEFAULT '0',
  `url` varchar(300) NOT NULL,
  `question_id` bigint(20) NOT NULL,
  `author_id` varchar(100) DEFAULT NULL,
  `content` longtext NOT NULL,
  `parise_num` int(11) NOT NULL,
  `comments_num` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime NOT NULL,
  `crawl_time` datetime NOT NULL,
  `crawl_update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`zhihu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;