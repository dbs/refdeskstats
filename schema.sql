--Table definition
CREATE TABLE refdeskstats (
    refdate DATE,
    reftime INTEGER,
    reftype TEXT,
    refcount_en INTEGER,
    refcount_fr INTEGER,
    create_time TIMESTAMP DEFAULT NOW()
);

--Primary Key
--This has caused problems in development. Still being looked into.
--ALTER TABLE refdeskstats ADD PRIMARY KEY (refdate, reftime, reftype);

--Permission
GRANT SELECT, INSERT, UPDATE, DELETE ON refstats TO refstats;

--View definition (most recent timestamps)
CREATE VIEW refstatview AS WITH x AS (
    SELECT reftime, reftype, refdate, MAX(create_time)
    AS create_time FROM refdeskstats
    GROUP BY reftime, reftype, refdate
    )
    SELECT x.reftime, x.reftype, x.refdate,
    x.create_time, r.refcount_en, r.refcount_fr
    FROM refstats r INNER JOIN x ON (
        x.create_time = r.create_time AND
        x.reftime = r.reftime AND
        x.reftype = r.reftype AND
        x.refdate = r.refdate
    )
    ORDER BY reftime, reftype
;

--View by days of the week.
CREATE VIEW refstatview_day_of_week AS
    SELECT reftime, reftype, refdate, 
    date_part('dow'::text, refdate) AS day_of_week,
    create_time, refcount_en, refcount_fr
    FROM refstatview
;
