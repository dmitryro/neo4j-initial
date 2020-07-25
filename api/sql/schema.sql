DO
$do$
BEGIN
   IF EXISTS (SELECT FROM pg_database WHERE datname = 'postgres') THEN
      RAISE NOTICE 'Database already exists';  -- optional
   ELSE
      PERFORM dblink_exec('dbname=' || current_database()  -- current db
                        , 'CREATE DATABASE postgres');
   END IF;
END
$do$;

ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'America/New_York';
GRANT ALL PRIVILEGES ON DATABASE postgres TO postgres;

CREATE SEQUENCE user_id_seq;

CREATE TABLE users (
        id integer NOT NULL DEFAULT nextval('user_id_seq'),
        username varchar(30) NOT NULL UNIQUE,
        category varchar(30),
        first_name varchar(30) NOT NULL,
        last_name varchar(30) NOT NULL,
        email varchar(75) NOT NULL,
        bio varchar(2048),
        password varchar(128) NOT NULL,
        is_staff BOOLEAN NOT NULL,
        is_active BOOLEAN NOT NULL,
        is_superuser BOOLEAN NOT NULL,
        last_login date NOT NULL,
        date_joined date NOT NULL
    );

CREATE SEQUENCE contact_id_seq;

CREATE TABLE contacts (
        id integer NOT NULL DEFAULT nextval('contact_id_seq'),
        username varchar(30) NOT NULL UNIQUE,
        first_name varchar(30) NOT NULL,
        last_name varchar(30) NOT NULL,
        email varchar(75) NOT NULL,
        phone varchar(30) NOT NULL
    );

CREATE SEQUENCE state_id_seq;

CREATE TABLE states (
        id integer NOT NULL DEFAULT nextval('state_id_seq'),
        name varchar(256) NOT NULL UNIQUE,
        code varchar(10) NOT NULL UNIQUE
    );


CREATE SEQUENCE site_id_seq;

CREATE TABLE sites (
        id integer NOT NULL DEFAULT nextval('site_id_seq'),
        host varchar(2048),
        ga varchar(50),
        port integer,
        ip varchar(256),
        date_added date NOT NULL,
        date_last_crawled date NOT NULL,
        UNIQUE(id)
   );


CREATE SEQUENCE page_id_seq;
 
CREATE TABLE pages (
        id integer NOT NULL DEFAULT nextval('page_id_seq'),
        name varchar(2048),
        meta varchar(2048),
        headers varchar(2048),
        site_id integer,
        FOREIGN KEY(site_id) REFERENCES sites(id) ON DELETE CASCADE,
        UNIQUE(id)        
    );

CREATE SEQUENCE form_id_seq;

CREATE TABLE forms (
        id integer NOT NULL DEFAULT nextval('form_id_seq'),
        action varchar(2048),
        form_id varchar(256),
        name varchar(256),
        method varchar(256),
        body varchar(2256),
        page_id integer NOT NULL,
        action_id integer,
        FOREIGN KEY(page_id) REFERENCES pages(id) ON DELETE CASCADE,
        UNIQUE(id)
    );

CREATE SEQUENCE formfield_id_seq;

CREATE TABLE formfields (
        id integer NOT NULL DEFAULT nextval('formfield_id_seq'),
        field_id varchar(256),
        field_name varchar(256),
        field_value varchar(256),
        field_type varchar(256),
        field_placeholder varchar(256),
        form_id integer NOT NULL,
        action_id integer,
        FOREIGN KEY(form_id) REFERENCES forms(id) ON DELETE CASCADE,
        UNIQUE(id)
    );

CREATE SEQUENCE rule_id_seq;

CREATE TABLE rules (
        id integer NOT NULL DEFAULT nextval('rule_id_seq'),
        is_active BOOLEAN DEFAULT TRUE,
        severety varchar(30),
        name varchar(256) NOT NULL,
        code varchar(256) NOT NULL,
        when_created date,
        UNIQUE(id)  
);

CREATE SEQUENCE action_id_seq;

CREATE TABLE actions (
        id integer NOT NULL DEFAULT nextval('action_id_seq'),
        is_running BOOLEAN DEFAULT FALSE,
        profile_key varchar(256) NOT NULL,
        name varchar(256) NOT NULL,
        last_run date NOT NULL,
        UNIQUE(id)        
);

CREATE SEQUENCE script_id_seq;

CREATE TABLE scripts (
        id integer NOT NULL DEFAULT nextval('script_id_seq'),
        profile_key varchar(256) NOT NULL,
        version float DEFAULT 1.0,
        code varchar(10000) NOT NULL,
        created_at date NOT NULL,
        UNIQUE(id)
);


CREATE TABLE action_rule_link (
        rule_id integer NOT NULL,
        action_id integer NOT NULL,
        FOREIGN KEY(rule_id) REFERENCES rules(id) ON DELETE CASCADE,
        FOREIGN KEY(action_id) REFERENCES actions(id) ON DELETE CASCADE
);

CREATE TABLE action_form_link (
        form_id integer NOT NULL,
        action_id integer NOT NULL,
        FOREIGN KEY(form_id) REFERENCES forms(id) ON DELETE CASCADE,
        FOREIGN KEY(action_id) REFERENCES actions(id) ON DELETE CASCADE        
);

CREATE TABLE action_formfield_link (
        formfield_id integer NOT NULL,
        action_id integer NOT NULL,
        FOREIGN KEY(formfield_id) REFERENCES formfields(id) ON DELETE CASCADE,
        FOREIGN KEY(action_id) REFERENCES actions(id) ON DELETE CASCADE
);

CREATE TABLE form_formfield_link (
        formfield_id integer NOT NULL,
        form_id integer NOT NULL,
        FOREIGN KEY(formfield_id) REFERENCES formfields(id) ON DELETE CASCADE,
        FOREIGN KEY(form_id) REFERENCES forms(id) ON DELETE CASCADE
);

CREATE SEQUENCE logtype_id_seq;

CREATE TABLE logtypes (
        id integer NOT NULL DEFAULT nextval('logtype_id_seq') UNIQUE,  
        type varchar(256) NOT NULL,
        code varchar(20) NOT NULL
);

CREATE TYPE importance as ENUM (
    'LOW',
    'MODERATE',
    'MEDIUM',
    'ELEVATED',
    'HIGH',
    'URGENT'
);

CREATE SEQUENCE logentry_id_seq;

CREATE TYPE severety AS ENUM (
  'LOW', 
  'MILD',
  'MEDIUM',
  'ELEVATED', 
  'HIGH',
  'DANGER',
  'SEVERE',
  'DISASTER');

CREATE SEQUENCE event_id_seq;

CREATE TABLE events(
       id integer NOT NULL DEFAULT nextval('event_id_seq') UNIQUE,
       recorded_at date NOT NULL,
       took_place_at date,
       title varchar(200),
       description varchar(1000),
       importance varchar(30), 
       severety varchar(30),
       action_id integer,
       field_id integer,
       FOREIGN KEY(action_id) REFERENCES actions(id) ON DELETE CASCADE
);

CREATE TABLE logentries (
        id integer NOT NULL DEFAULT nextval('logentry_id_seq'),
        severety varchar(30),
        recorded_at date NOT NULL,
        header varchar(200),
        ip varchar(30) DEFAULT '0.0.0.0',
        body varchar(1500),
        type_id integer NOT NULL,
        profile_key varchar(30) NOT NULL,
        action_id integer,
        event_id integer,
        FOREIGN KEY(event_id) REFERENCES events(id) ON DELETE CASCADE,
        FOREIGN KEY(type_id) REFERENCES logtypes(id) ON DELETE CASCADE,
        FOREIGN KEY(action_id) REFERENCES actions(id) ON DELETE CASCADE
);


ALTER SEQUENCE event_id_seq
OWNED BY events.id;

ALTER SEQUENCE logentry_id_seq
OWNED BY logentries.id;

ALTER SEQUENCE logtype_id_seq
OWNED BY logtypes.id;

ALTER SEQUENCE script_id_seq
OWNED BY scripts.id;

ALTER SEQUENCE rule_id_seq
OWNED BY rules.id;

ALTER SEQUENCE formfield_id_seq 
OWNED BY formfields.id;

ALTER SEQUENCE form_id_seq 
OWNED BY forms.id;

ALTER SEQUENCE page_id_seq 
OWNED BY pages.id;

ALTER SEQUENCE site_id_seq 
OWNED BY sites.id;

ALTER SEQUENCE user_id_seq
OWNED BY users.id;

ALTER SEQUENCE state_id_seq
OWNED BY states.id;

ALTER SEQUENCE contact_id_seq
OWNED BY contacts.id;

ALTER SEQUENCE action_id_seq
OWNED BY actions.id;
