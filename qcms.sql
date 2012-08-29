SET NAMES utf8;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
--  Table structure for `qc_article`
-- ----------------------------
DROP TABLE IF EXISTS `qc_article`;
CREATE TABLE `qc_article` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `model_id` int(11) DEFAULT NULL,
  `locale_id` int(11) DEFAULT NULL,
  `category_has_article_id` int(11) DEFAULT NULL,
  `ip` varchar(15) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `time` int(11) NOT NULL,
  `change_time` int(11) NOT NULL,
  `listorder` int(11) NOT NULL DEFAULT '0',
  `title` varchar(255) DEFAULT NULL,
  `keywords` varchar(255) DEFAULT NULL,
  `description` text,
  `content` text,
  `avatar` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `IX_model_locale` (`model_id`,`locale_id`,`category_has_article_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `qc_attachment`
-- ----------------------------
DROP TABLE IF EXISTS `qc_attachment`;
CREATE TABLE `qc_attachment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `url` varchar(255) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `info` varchar(255) DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `type` varchar(45) DEFAULT NULL COMMENT '类型: jpg,png,zip,doc',
  `ip` varchar(15) DEFAULT NULL,
  `time` int(11) DEFAULT NULL COMMENT '上传时间',
  `size` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=72 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `qc_category`
-- ----------------------------
DROP TABLE IF EXISTS `qc_category`;
CREATE TABLE `qc_category` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `parent` int(11) NOT NULL DEFAULT '0' COMMENT '父级ID',
  `parents` mediumtext NOT NULL COMMENT '所有上级分类的ID',
  `childs` mediumtext NOT NULL COMMENT '所有下级分类的ID',
  `listorder` smallint(5) NOT NULL DEFAULT '0',
  `model_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `IX_listorder` (`listorder`),
  KEY `FK_C_M_M_idx` (`model_id`),
  CONSTRAINT `FK_C_M_M` FOREIGN KEY (`model_id`) REFERENCES `qc_model` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `qc_category`
-- ----------------------------
BEGIN;
INSERT INTO `qc_category` VALUES ('1', '0', ',0,', ',', '0', '1');
COMMIT;

-- ----------------------------
--  Table structure for `qc_category_has_article`
-- ----------------------------
DROP TABLE IF EXISTS `qc_category_has_article`;
CREATE TABLE `qc_category_has_article` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `category_id` (`category_id`),
  CONSTRAINT `FK_C_H_A` FOREIGN KEY (`category_id`) REFERENCES `qc_category` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Table structure for `qc_category_locale`
-- ----------------------------
DROP TABLE IF EXISTS `qc_category_locale`;
CREATE TABLE `qc_category_locale` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `category_id` int(11) NOT NULL,
  `locale_id` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `info` varchar(355) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `FK_CL_C_idx` (`category_id`),
  KEY `FK_CL_L_idx` (`locale_id`),
  CONSTRAINT `FK_CL_C` FOREIGN KEY (`category_id`) REFERENCES `qc_category` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_CL_L` FOREIGN KEY (`locale_id`) REFERENCES `qc_locale` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `qc_category_locale`
-- ----------------------------
BEGIN;
INSERT INTO `qc_category_locale` VALUES ('1', '1', '1', 'news', null), ('2', '1', '2', '新闻中心', null);
COMMIT;

-- ----------------------------
--  Table structure for `qc_locale`
-- ----------------------------
DROP TABLE IF EXISTS `qc_locale`;
CREATE TABLE `qc_locale` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(45) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `qc_locale`
-- ----------------------------
BEGIN;
INSERT INTO `qc_locale` VALUES ('1', 'EN', 'English'), ('2', 'ZH_CN', '简体中文');
COMMIT;

-- ----------------------------
--  Table structure for `qc_model`
-- ----------------------------
DROP TABLE IF EXISTS `qc_model`;
CREATE TABLE `qc_model` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` varchar(100) NOT NULL,
  `info` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `qc_model`
-- ----------------------------
BEGIN;
INSERT INTO `qc_model` VALUES ('1', 'article', '文章');
COMMIT;

-- ----------------------------
--  Table structure for `qc_model_data`
-- ----------------------------
DROP TABLE IF EXISTS `qc_model_data`;
CREATE TABLE `qc_model_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `model_id` int(11) NOT NULL,
  `widget` varchar(45) NOT NULL COMMENT '表单元素类型',
  `type` varchar(45) NOT NULL COMMENT '字段类型',
  `name` varchar(45) NOT NULL COMMENT '字段名',
  `label` varchar(45) NOT NULL COMMENT '标签',
  `info` varchar(255) DEFAULT NULL,
  `data` text COMMENT '可选数据列表,格式:\\nid:label\\nid:label',
  `validators` text COMMENT '验证规则',
  `filters` text COMMENT '过滤规则',
  `listorder` int(11) DEFAULT NULL,
  `max_len` int(11) NOT NULL DEFAULT '0' COMMENT '最大长度,0为不限',
  `min_len` int(11) NOT NULL DEFAULT '0' COMMENT '最小长度,0为不限',
  PRIMARY KEY (`id`),
  KEY `FK_MD_M_idx` (`model_id`),
  CONSTRAINT `FK_MD_M` FOREIGN KEY (`model_id`) REFERENCES `qc_model` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `qc_model_data`
-- ----------------------------
BEGIN;
INSERT INTO `qc_model_data` VALUES ('1', '1', 'Text', 'VARCHAR', 'title', '标题', null, null, '[\"notEmpty\"]', '[\"trim\"]', null, '255', '0'), ('2', '1', 'Text', 'VARCHAR', 'keywords', '关键字', null, null, null, '[\"trim\"]', null, '255', '0'), ('3', '1', 'Textarea', 'TEXT', 'description', '简介', null, null, null, '[\"toText\"]', null, '0', '0'), ('4', '1', 'Editor', 'TEXT', 'content', '内容', null, null, null, null, null, '0', '0'), ('5', '1', 'ImageUpload', 'VARCHAR', 'avatar', '封面', null, null, null, null, null, '255', '0');
COMMIT;

-- ----------------------------
--  Table structure for `qc_role`
-- ----------------------------
DROP TABLE IF EXISTS `qc_role`;
CREATE TABLE `qc_role` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(45) NOT NULL,
  `info` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `IX_code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `qc_role`
-- ----------------------------
BEGIN;
INSERT INTO `qc_role` VALUES ('1', 'admin', '管理员'), ('2', 'user', '注册会员');
COMMIT;

-- ----------------------------
--  Table structure for `qc_role_has_user`
-- ----------------------------
DROP TABLE IF EXISTS `qc_role_has_user`;
CREATE TABLE `qc_role_has_user` (
  `user_id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`,`role_id`),
  KEY `FK_RHU_U_idx` (`user_id`),
  KEY `FK_RHR_R_idx` (`role_id`),
  CONSTRAINT `FK_RHU_U` FOREIGN KEY (`user_id`) REFERENCES `qc_user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_RHR_R` FOREIGN KEY (`role_id`) REFERENCES `qc_role` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `qc_role_has_user`
-- ----------------------------
BEGIN;
INSERT INTO `qc_role_has_user` VALUES ('3', '1'), ('3', '2');
COMMIT;

-- ----------------------------
--  Table structure for `qc_user`
-- ----------------------------
DROP TABLE IF EXISTS `qc_user`;
CREATE TABLE `qc_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(45) DEFAULT NULL,
  `email` varchar(255) DEFAULT NULL,
  `password` varchar(32) NOT NULL,
  `time` int(11) DEFAULT NULL COMMENT '注册时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `qc_user`
-- ----------------------------
BEGIN;
INSERT INTO `qc_user` VALUES ('3', 'admin', 'admin@admin.com', '23eeeb4347bdd26bfc6b7ee9a3b755dd', '1345443175');
COMMIT;

-- ----------------------------
--  Table structure for `qc_plugin`
-- ----------------------------
DROP TABLE IF EXISTS `qc_plugin`;
CREATE TABLE `qc_plugin` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `bind` text,
  `config` text,
  PRIMARY KEY (`id`),
  KEY `IX_plugin` (`name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
--  Records of `qc_plugin`
-- ----------------------------
BEGIN;
INSERT INTO `qc_plugin` VALUES ('1', 'editor_kind', '[{\"action\": \"bindEditor\", \"target\": \"app.controller.admin.contentAdd\", \"event\": \"beforeRender\"}, {\"action\": \"bindEditor\", \"target\": \"app.controller.admin.contentEdit\", \"event\": \"beforeRender\"}]', '\"{}\"');
COMMIT;


SET FOREIGN_KEY_CHECKS = 1;
