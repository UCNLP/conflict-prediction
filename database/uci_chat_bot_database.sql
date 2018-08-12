
/* 1. Create Database */
create database uci_chat_bot;
use uci_chat_bot;

/* 2. create table working_table */
CREATE TABLE `working_table` (
	`project_name` VARCHAR(50) NOT NULL,
	`file_name` VARCHAR(50) NOT NULL,
	`logic_name` VARCHAR(50) NOT NULL,
	`user_name` VARCHAR(50) NOT NULL,
	`work_line` INT(11) NULL DEFAULT NULL,
	`work_amount` INT(11) NULL DEFAULT NULL,
	`log_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`project_name`, `file_name`, `logic_name`, `user_name`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;


/* 3. create table conflict_table */
CREATE TABLE `conflict_table` (
	`project_name` VARCHAR(50) NOT NULL,
	`file_name` VARCHAR(50) NOT NULL,
	`logic1_name` VARCHAR(50) NOT NULL,
	`logic2_name` VARCHAR(50) NOT NULL,
	`user1_name` VARCHAR(50) NOT NULL,
	`user2_name` VARCHAR(50) NOT NULL,
	`alert_count` INT(11) NULL DEFAULT '1',
	`severity` INT(11) NULL DEFAULT '1',
	`log_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`project_name`, `file_name`, `logic1_name`, `user1_name`, `user2_name`, `logic2_name`)
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;

/* 4. create user_table */
CREATE TABLE `user_table` (
	`git_id` VARCHAR(30) NOT NULL,
	`slack_id` VARCHAR(30) NOT NULL
)
COLLATE='utf8_general_ci'
ENGINE=InnoDB
;
