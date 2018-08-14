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
  `author_name` varchar(100) DEFAULT NULL,
  `content` longtext NOT NULL,
  `praise_num` int(11) NOT NULL,
  `comments_num` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime NOT NULL,
  `crawl_time` datetime NOT NULL,
  `crawl_update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`zhihu_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `scrapy-spider`.`lagou_job` (
  `url_object_id` varchar(50) NOT NULL,
  `url` varchar(300) NOT NULL,
  `title` varchar(100) NOT NULL,
  `salary_min` varchar(20) DEFAULT NULL,
  `salary_max` varchar(20) DEFAULT NULL,
  `job_city` varchar(10) DEFAULT NULL,
  `work_years_min` varchar(100) DEFAULT NULL,
  `work_years_max` varchar(100) DEFAULT NULL,
  `degree_need` varchar(30) DEFAULT NULL,
  `job_type` varchar(20) DEFAULT NULL,
  `publish_time` varchar(20) DEFAULT NULL,
  `tags` varchar(100) DEFAULT NULL,
  `job_advantage` longtext,
  `job_desc` longtext,
  `job_addr` varchar(255) DEFAULT NULL,
  `company_name` varchar(100) DEFAULT NULL,
  `company_url` varchar(300) DEFAULT NULL,
  `crawl_time` datetime DEFAULT NULL,
  `crawl_update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`url_object_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE `scrapy-spider`.`proxy_ip` (
  `ip` VARCHAR(20) NOT NULL,
  `port` INT(11) NULL,
  `speed` FLOAT NULL,
  `proxy_type` CHAR(5) NULL,
  PRIMARY KEY (`ip`));
