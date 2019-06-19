-- ---
-- Table 'results'
--
-- ---

DROP TABLE IF EXISTS results;

CREATE TABLE results (
	id       SERIAL PRIMARY KEY,
	taken    DATE,
	code     VARCHAR(6),
	name     VARCHAR,
	failures INTEGER,
	threes   INTEGER,
	fours    INTEGER,
	fives    INTEGER,
	exam     BYTEA,
	solution BYTEA
);

-- ---
-- Table 'exam_suggestions'
--
-- ---

DROP TABLE IF EXISTS exam_suggestions;

CREATE TABLE exam_suggestions (
	id        SERIAL PRIMARY KEY,
	taken     DATE,
	code      VARCHAR(6),
	exam      BYTEA,
	solution  BYTEA
);
