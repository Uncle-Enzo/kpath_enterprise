--
-- PostgreSQL database dump
--

-- Dumped from database version 17.4 (Homebrew)
-- Dumped by pg_dump version 17.0

-- Started on 2025-06-13 14:30:04 CEST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 3 (class 3079 OID 16595)
-- Name: pg_trgm; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pg_trgm WITH SCHEMA public;


--
-- TOC entry 4058 (class 0 OID 0)
-- Dependencies: 3
-- Name: EXTENSION pg_trgm; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pg_trgm IS 'text similarity measurement and index searching based on trigrams';


--
-- TOC entry 2 (class 3079 OID 16584)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- TOC entry 4059 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- TOC entry 298 (class 1255 OID 16950)
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: james
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO james;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 230 (class 1259 OID 16753)
-- Name: access_policy; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.access_policy (
    id integer NOT NULL,
    service_id integer,
    conditions jsonb NOT NULL,
    type text,
    priority integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT access_policy_type_check CHECK ((type = ANY (ARRAY['RBAC'::text, 'ABAC'::text])))
);


ALTER TABLE public.access_policy OWNER TO james;

--
-- TOC entry 229 (class 1259 OID 16752)
-- Name: access_policy_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.access_policy_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.access_policy_id_seq OWNER TO james;

--
-- TOC entry 4060 (class 0 OID 0)
-- Dependencies: 229
-- Name: access_policy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.access_policy_id_seq OWNED BY public.access_policy.id;


--
-- TOC entry 243 (class 1259 OID 16862)
-- Name: api_keys; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.api_keys (
    id integer NOT NULL,
    key_hash text NOT NULL,
    user_id integer,
    name text,
    scopes text[],
    expires_at timestamp without time zone,
    last_used timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    active boolean DEFAULT true
);


ALTER TABLE public.api_keys OWNER TO james;

--
-- TOC entry 242 (class 1259 OID 16861)
-- Name: api_keys_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.api_keys_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.api_keys_id_seq OWNER TO james;

--
-- TOC entry 4061 (class 0 OID 0)
-- Dependencies: 242
-- Name: api_keys_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.api_keys_id_seq OWNED BY public.api_keys.id;


--
-- TOC entry 234 (class 1259 OID 16780)
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    user_id integer,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    action text NOT NULL,
    payload jsonb,
    ip_address inet
);


ALTER TABLE public.audit_logs OWNER TO james;

--
-- TOC entry 233 (class 1259 OID 16779)
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO james;

--
-- TOC entry 4062 (class 0 OID 0)
-- Dependencies: 233
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- TOC entry 237 (class 1259 OID 16815)
-- Name: cache_entries; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.cache_entries (
    key text NOT NULL,
    value jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    expires_at timestamp without time zone,
    hit_count integer DEFAULT 0
);


ALTER TABLE public.cache_entries OWNER TO james;

--
-- TOC entry 232 (class 1259 OID 16770)
-- Name: faiss_index_metadata; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.faiss_index_metadata (
    id integer NOT NULL,
    index_name text,
    last_updated timestamp without time zone,
    embedding_model text,
    total_vectors integer,
    index_params jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.faiss_index_metadata OWNER TO james;

--
-- TOC entry 4063 (class 0 OID 0)
-- Dependencies: 232
-- Name: TABLE faiss_index_metadata; Type: COMMENT; Schema: public; Owner: james
--

COMMENT ON TABLE public.faiss_index_metadata IS 'Metadata about FAISS vector indexes';


--
-- TOC entry 231 (class 1259 OID 16769)
-- Name: faiss_index_metadata_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.faiss_index_metadata_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.faiss_index_metadata_id_seq OWNER TO james;

--
-- TOC entry 4064 (class 0 OID 0)
-- Dependencies: 231
-- Name: faiss_index_metadata_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.faiss_index_metadata_id_seq OWNED BY public.faiss_index_metadata.id;


--
-- TOC entry 236 (class 1259 OID 16795)
-- Name: feedback_log; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.feedback_log (
    id integer NOT NULL,
    query text NOT NULL,
    query_embedding_hash text,
    selected_service_id integer,
    "timestamp" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    user_id integer,
    rank_position integer,
    click_through boolean DEFAULT true
);


ALTER TABLE public.feedback_log OWNER TO james;

--
-- TOC entry 4065 (class 0 OID 0)
-- Dependencies: 236
-- Name: TABLE feedback_log; Type: COMMENT; Schema: public; Owner: james
--

COMMENT ON TABLE public.feedback_log IS 'User feedback for improving search rankings';


--
-- TOC entry 235 (class 1259 OID 16794)
-- Name: feedback_log_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.feedback_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.feedback_log_id_seq OWNER TO james;

--
-- TOC entry 4066 (class 0 OID 0)
-- Dependencies: 235
-- Name: feedback_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.feedback_log_id_seq OWNED BY public.feedback_log.id;


--
-- TOC entry 247 (class 1259 OID 16898)
-- Name: integration_configs; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.integration_configs (
    id integer NOT NULL,
    type text NOT NULL,
    name text NOT NULL,
    config jsonb NOT NULL,
    enabled boolean DEFAULT true,
    last_sync timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.integration_configs OWNER TO james;

--
-- TOC entry 246 (class 1259 OID 16897)
-- Name: integration_configs_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.integration_configs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.integration_configs_id_seq OWNER TO james;

--
-- TOC entry 4067 (class 0 OID 0)
-- Dependencies: 246
-- Name: integration_configs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.integration_configs_id_seq OWNED BY public.integration_configs.id;


--
-- TOC entry 224 (class 1259 OID 16707)
-- Name: interaction_capability; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.interaction_capability (
    id integer NOT NULL,
    service_id integer,
    interaction_desc text NOT NULL,
    interaction_type text,
    CONSTRAINT interaction_capability_interaction_type_check CHECK ((interaction_type = ANY (ARRAY['sync'::text, 'async'::text, 'stream'::text, 'batch'::text])))
);


ALTER TABLE public.interaction_capability OWNER TO james;

--
-- TOC entry 223 (class 1259 OID 16706)
-- Name: interaction_capability_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.interaction_capability_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.interaction_capability_id_seq OWNER TO james;

--
-- TOC entry 4068 (class 0 OID 0)
-- Dependencies: 223
-- Name: interaction_capability_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.interaction_capability_id_seq OWNED BY public.interaction_capability.id;


--
-- TOC entry 245 (class 1259 OID 16880)
-- Name: query_templates; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.query_templates (
    id integer NOT NULL,
    name text NOT NULL,
    template text NOT NULL,
    parameters jsonb,
    description text,
    created_by integer,
    is_public boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.query_templates OWNER TO james;

--
-- TOC entry 244 (class 1259 OID 16879)
-- Name: query_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.query_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.query_templates_id_seq OWNER TO james;

--
-- TOC entry 4069 (class 0 OID 0)
-- Dependencies: 244
-- Name: query_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.query_templates_id_seq OWNED BY public.query_templates.id;


--
-- TOC entry 253 (class 1259 OID 17206)
-- Name: service_agent_protocols; Type: TABLE; Schema: public; Owner: ai_user
--

CREATE TABLE public.service_agent_protocols (
    id integer NOT NULL,
    service_id integer,
    message_protocol character varying(100) NOT NULL,
    protocol_version character varying(20),
    expected_input_format text,
    response_style character varying(50),
    message_examples jsonb,
    tool_schema jsonb,
    input_validation_rules jsonb,
    output_parsing_rules jsonb,
    requires_session_state boolean DEFAULT false,
    max_context_length integer,
    supported_languages text[],
    supports_streaming boolean DEFAULT false,
    supports_async boolean DEFAULT false,
    supports_batch boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.service_agent_protocols OWNER TO ai_user;

--
-- TOC entry 252 (class 1259 OID 17205)
-- Name: service_agent_protocols_id_seq; Type: SEQUENCE; Schema: public; Owner: ai_user
--

CREATE SEQUENCE public.service_agent_protocols_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_agent_protocols_id_seq OWNER TO ai_user;

--
-- TOC entry 4070 (class 0 OID 0)
-- Dependencies: 252
-- Name: service_agent_protocols_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ai_user
--

ALTER SEQUENCE public.service_agent_protocols_id_seq OWNED BY public.service_agent_protocols.id;


--
-- TOC entry 222 (class 1259 OID 16692)
-- Name: service_capability; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.service_capability (
    id integer NOT NULL,
    service_id integer,
    capability_desc text NOT NULL,
    capability_name text,
    input_schema jsonb,
    output_schema jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.service_capability OWNER TO james;

--
-- TOC entry 4071 (class 0 OID 0)
-- Dependencies: 222
-- Name: TABLE service_capability; Type: COMMENT; Schema: public; Owner: james
--

COMMENT ON TABLE public.service_capability IS 'Individual capabilities exposed by each service';


--
-- TOC entry 221 (class 1259 OID 16691)
-- Name: service_capability_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.service_capability_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_capability_id_seq OWNER TO james;

--
-- TOC entry 4072 (class 0 OID 0)
-- Dependencies: 221
-- Name: service_capability_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.service_capability_id_seq OWNED BY public.service_capability.id;


--
-- TOC entry 241 (class 1259 OID 16844)
-- Name: service_health; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.service_health (
    id integer NOT NULL,
    service_id integer,
    health_status text,
    last_check timestamp without time zone,
    response_time_ms integer,
    error_count integer DEFAULT 0,
    consecutive_failures integer DEFAULT 0,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT service_health_health_status_check CHECK ((health_status = ANY (ARRAY['healthy'::text, 'degraded'::text, 'unhealthy'::text, 'unknown'::text])))
);


ALTER TABLE public.service_health OWNER TO james;

--
-- TOC entry 240 (class 1259 OID 16843)
-- Name: service_health_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.service_health_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_health_id_seq OWNER TO james;

--
-- TOC entry 4073 (class 0 OID 0)
-- Dependencies: 240
-- Name: service_health_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.service_health_id_seq OWNED BY public.service_health.id;


--
-- TOC entry 255 (class 1259 OID 17227)
-- Name: service_industries; Type: TABLE; Schema: public; Owner: ai_user
--

CREATE TABLE public.service_industries (
    id integer NOT NULL,
    service_id integer,
    industry character varying(100) NOT NULL,
    relevance_score double precision DEFAULT 1.0,
    use_cases text[]
);


ALTER TABLE public.service_industries OWNER TO ai_user;

--
-- TOC entry 254 (class 1259 OID 17226)
-- Name: service_industries_id_seq; Type: SEQUENCE; Schema: public; Owner: ai_user
--

CREATE SEQUENCE public.service_industries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_industries_id_seq OWNER TO ai_user;

--
-- TOC entry 4074 (class 0 OID 0)
-- Dependencies: 254
-- Name: service_industries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ai_user
--

ALTER SEQUENCE public.service_industries_id_seq OWNED BY public.service_industries.id;


--
-- TOC entry 226 (class 1259 OID 16722)
-- Name: service_industry; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.service_industry (
    id integer NOT NULL,
    service_id integer,
    domain text NOT NULL
);


ALTER TABLE public.service_industry OWNER TO james;

--
-- TOC entry 225 (class 1259 OID 16721)
-- Name: service_industry_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.service_industry_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_industry_id_seq OWNER TO james;

--
-- TOC entry 4075 (class 0 OID 0)
-- Dependencies: 225
-- Name: service_industry_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.service_industry_id_seq OWNED BY public.service_industry.id;


--
-- TOC entry 251 (class 1259 OID 17186)
-- Name: service_integration_details; Type: TABLE; Schema: public; Owner: ai_user
--

CREATE TABLE public.service_integration_details (
    id integer NOT NULL,
    service_id integer,
    access_protocol character varying(50) NOT NULL,
    base_endpoint text,
    auth_method character varying(50),
    auth_config jsonb,
    auth_endpoint text,
    rate_limit_requests integer,
    rate_limit_window_seconds integer,
    max_concurrent_requests integer,
    circuit_breaker_config jsonb,
    default_headers jsonb,
    request_content_type character varying(100) DEFAULT 'application/json'::character varying,
    response_content_type character varying(100) DEFAULT 'application/json'::character varying,
    request_transform jsonb,
    response_transform jsonb,
    esb_type character varying(50),
    esb_service_name text,
    esb_routing_key text,
    esb_operation text,
    esb_adapter_type character varying(50),
    esb_namespace text,
    esb_version character varying(20),
    health_check_endpoint text,
    health_check_interval_seconds integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.service_integration_details OWNER TO ai_user;

--
-- TOC entry 250 (class 1259 OID 17185)
-- Name: service_integration_details_id_seq; Type: SEQUENCE; Schema: public; Owner: ai_user
--

CREATE SEQUENCE public.service_integration_details_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_integration_details_id_seq OWNER TO ai_user;

--
-- TOC entry 4076 (class 0 OID 0)
-- Dependencies: 250
-- Name: service_integration_details_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ai_user
--

ALTER SEQUENCE public.service_integration_details_id_seq OWNED BY public.service_integration_details.id;


--
-- TOC entry 239 (class 1259 OID 16825)
-- Name: service_versions; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.service_versions (
    id integer NOT NULL,
    service_id integer,
    version text NOT NULL,
    version_tag text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    deprecated boolean DEFAULT false,
    deprecated_at timestamp without time zone,
    sunset_at timestamp without time zone,
    compatible_with text[],
    breaking_changes text[],
    migration_notes text,
    release_notes text,
    CONSTRAINT service_versions_version_tag_check CHECK ((version_tag = ANY (ARRAY['stable'::text, 'beta'::text, 'alpha'::text, 'deprecated'::text])))
);


ALTER TABLE public.service_versions OWNER TO james;

--
-- TOC entry 238 (class 1259 OID 16824)
-- Name: service_versions_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.service_versions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.service_versions_id_seq OWNER TO james;

--
-- TOC entry 4077 (class 0 OID 0)
-- Dependencies: 238
-- Name: service_versions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.service_versions_id_seq OWNED BY public.service_versions.id;


--
-- TOC entry 220 (class 1259 OID 16677)
-- Name: services; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.services (
    id integer NOT NULL,
    name text NOT NULL,
    description text NOT NULL,
    endpoint text,
    version text,
    status text DEFAULT 'active'::text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    tool_type character varying(50) DEFAULT 'API'::character varying,
    interaction_modes text[],
    visibility character varying(20) DEFAULT 'internal'::character varying,
    deprecation_date timestamp without time zone,
    deprecation_notice text,
    success_criteria jsonb,
    default_timeout_ms integer DEFAULT 30000,
    default_retry_policy jsonb,
    CONSTRAINT check_tool_type CHECK (((tool_type)::text = ANY ((ARRAY['InternalAgent'::character varying, 'ExternalAgent'::character varying, 'API'::character varying, 'LegacySystem'::character varying, 'ESBEndpoint'::character varying, 'MicroService'::character varying])::text[]))),
    CONSTRAINT check_visibility CHECK (((visibility)::text = ANY ((ARRAY['internal'::character varying, 'org-wide'::character varying, 'public'::character varying, 'restricted'::character varying])::text[]))),
    CONSTRAINT services_status_check CHECK ((status = ANY (ARRAY['active'::text, 'inactive'::text, 'deprecated'::text])))
);


ALTER TABLE public.services OWNER TO james;

--
-- TOC entry 4078 (class 0 OID 0)
-- Dependencies: 220
-- Name: TABLE services; Type: COMMENT; Schema: public; Owner: james
--

COMMENT ON TABLE public.services IS 'Core service registry storing all discoverable services';


--
-- TOC entry 219 (class 1259 OID 16676)
-- Name: services_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.services_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.services_id_seq OWNER TO james;

--
-- TOC entry 4079 (class 0 OID 0)
-- Dependencies: 219
-- Name: services_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.services_id_seq OWNED BY public.services.id;


--
-- TOC entry 249 (class 1259 OID 16911)
-- Name: user_selections; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.user_selections (
    id integer NOT NULL,
    search_id uuid DEFAULT public.uuid_generate_v4(),
    query text NOT NULL,
    query_embedding_hash text,
    selected_service_id integer,
    result_position integer NOT NULL,
    selection_time_ms integer,
    session_id uuid,
    user_satisfaction boolean,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_selections OWNER TO james;

--
-- TOC entry 248 (class 1259 OID 16910)
-- Name: user_selections_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.user_selections_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_selections_id_seq OWNER TO james;

--
-- TOC entry 4080 (class 0 OID 0)
-- Dependencies: 248
-- Name: user_selections_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.user_selections_id_seq OWNED BY public.user_selections.id;


--
-- TOC entry 228 (class 1259 OID 16738)
-- Name: users; Type: TABLE; Schema: public; Owner: james
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email text NOT NULL,
    role text,
    org_id integer,
    attributes jsonb DEFAULT '{}'::jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    password_hash text,
    is_active boolean DEFAULT true,
    username character varying,
    CONSTRAINT users_role_check CHECK ((role = ANY (ARRAY['admin'::text, 'editor'::text, 'viewer'::text, 'user'::text])))
);


ALTER TABLE public.users OWNER TO james;

--
-- TOC entry 4081 (class 0 OID 0)
-- Dependencies: 228
-- Name: TABLE users; Type: COMMENT; Schema: public; Owner: james
--

COMMENT ON TABLE public.users IS 'System users with role-based access control';


--
-- TOC entry 227 (class 1259 OID 16737)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: james
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO james;

--
-- TOC entry 4082 (class 0 OID 0)
-- Dependencies: 227
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: james
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 256 (class 1259 OID 17243)
-- Name: v_service_full_details; Type: VIEW; Schema: public; Owner: ai_user
--

CREATE VIEW public.v_service_full_details AS
 SELECT s.id,
    s.name,
    s.description,
    s.tool_type,
    s.interaction_modes,
    s.visibility,
    s.version,
    s.status,
    s.default_timeout_ms,
    sid.access_protocol,
    sid.base_endpoint,
    sid.auth_method,
    sid.rate_limit_requests,
    sid.esb_type,
    sid.esb_service_name,
    sap.message_protocol,
    sap.response_style,
    sap.supports_streaming,
    count(DISTINCT sc.id) AS capability_count,
    count(DISTINCT si.id) AS industry_count
   FROM ((((public.services s
     LEFT JOIN public.service_integration_details sid ON ((s.id = sid.service_id)))
     LEFT JOIN public.service_agent_protocols sap ON ((s.id = sap.service_id)))
     LEFT JOIN public.service_capability sc ON ((s.id = sc.service_id)))
     LEFT JOIN public.service_industries si ON ((s.id = si.service_id)))
  GROUP BY s.id, s.name, s.description, s.tool_type, s.interaction_modes, s.visibility, s.version, s.status, s.default_timeout_ms, sid.access_protocol, sid.base_endpoint, sid.auth_method, sid.rate_limit_requests, sid.esb_type, sid.esb_service_name, sap.message_protocol, sap.response_style, sap.supports_streaming;


ALTER VIEW public.v_service_full_details OWNER TO ai_user;

--
-- TOC entry 3717 (class 2604 OID 16756)
-- Name: access_policy id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.access_policy ALTER COLUMN id SET DEFAULT nextval('public.access_policy_id_seq'::regclass);


--
-- TOC entry 3736 (class 2604 OID 16865)
-- Name: api_keys id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.api_keys ALTER COLUMN id SET DEFAULT nextval('public.api_keys_id_seq'::regclass);


--
-- TOC entry 3722 (class 2604 OID 16783)
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- TOC entry 3720 (class 2604 OID 16773)
-- Name: faiss_index_metadata id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.faiss_index_metadata ALTER COLUMN id SET DEFAULT nextval('public.faiss_index_metadata_id_seq'::regclass);


--
-- TOC entry 3724 (class 2604 OID 16798)
-- Name: feedback_log id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.feedback_log ALTER COLUMN id SET DEFAULT nextval('public.feedback_log_id_seq'::regclass);


--
-- TOC entry 3742 (class 2604 OID 16901)
-- Name: integration_configs id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.integration_configs ALTER COLUMN id SET DEFAULT nextval('public.integration_configs_id_seq'::regclass);


--
-- TOC entry 3710 (class 2604 OID 16710)
-- Name: interaction_capability id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.interaction_capability ALTER COLUMN id SET DEFAULT nextval('public.interaction_capability_id_seq'::regclass);


--
-- TOC entry 3739 (class 2604 OID 16883)
-- Name: query_templates id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.query_templates ALTER COLUMN id SET DEFAULT nextval('public.query_templates_id_seq'::regclass);


--
-- TOC entry 3753 (class 2604 OID 17209)
-- Name: service_agent_protocols id; Type: DEFAULT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.service_agent_protocols ALTER COLUMN id SET DEFAULT nextval('public.service_agent_protocols_id_seq'::regclass);


--
-- TOC entry 3708 (class 2604 OID 16695)
-- Name: service_capability id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.service_capability ALTER COLUMN id SET DEFAULT nextval('public.service_capability_id_seq'::regclass);


--
-- TOC entry 3732 (class 2604 OID 16847)
-- Name: service_health id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.service_health ALTER COLUMN id SET DEFAULT nextval('public.service_health_id_seq'::regclass);


--
-- TOC entry 3759 (class 2604 OID 17230)
-- Name: service_industries id; Type: DEFAULT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.service_industries ALTER COLUMN id SET DEFAULT nextval('public.service_industries_id_seq'::regclass);


--
-- TOC entry 3711 (class 2604 OID 16725)
-- Name: service_industry id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.service_industry ALTER COLUMN id SET DEFAULT nextval('public.service_industry_id_seq'::regclass);


--
-- TOC entry 3748 (class 2604 OID 17189)
-- Name: service_integration_details id; Type: DEFAULT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.service_integration_details ALTER COLUMN id SET DEFAULT nextval('public.service_integration_details_id_seq'::regclass);


--
-- TOC entry 3729 (class 2604 OID 16828)
-- Name: service_versions id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.service_versions ALTER COLUMN id SET DEFAULT nextval('public.service_versions_id_seq'::regclass);


--
-- TOC entry 3701 (class 2604 OID 16680)
-- Name: services id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.services ALTER COLUMN id SET DEFAULT nextval('public.services_id_seq'::regclass);


--
-- TOC entry 3745 (class 2604 OID 16914)
-- Name: user_selections id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.user_selections ALTER COLUMN id SET DEFAULT nextval('public.user_selections_id_seq'::regclass);


--
-- TOC entry 3712 (class 2604 OID 16741)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 4027 (class 0 OID 16753)
-- Dependencies: 230
-- Data for Name: access_policy; Type: TABLE DATA; Schema: public; Owner: james
--



--
-- TOC entry 4040 (class 0 OID 16862)
-- Dependencies: 243
-- Data for Name: api_keys; Type: TABLE DATA; Schema: public; Owner: james
--



--
-- TOC entry 4031 (class 0 OID 16780)
-- Dependencies: 234
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: james
--



--
-- TOC entry 4034 (class 0 OID 16815)
-- Dependencies: 237
-- Data for Name: cache_entries; Type: TABLE DATA; Schema: public; Owner: james
--



--
-- TOC entry 4029 (class 0 OID 16770)
-- Dependencies: 232
-- Data for Name: faiss_index_metadata; Type: TABLE DATA; Schema: public; Owner: james
--



--
-- TOC entry 4033 (class 0 OID 16795)
-- Dependencies: 236
-- Data for Name: feedback_log; Type: TABLE DATA; Schema: public; Owner: james
--



--
-- TOC entry 4044 (class 0 OID 16898)
-- Dependencies: 247
-- Data for Name: integration_configs; Type: TABLE DATA; Schema: public; Owner: james
--



--
-- TOC entry 4021 (class 0 OID 16707)
-- Dependencies: 224
-- Data for Name: interaction_capability; Type: TABLE DATA; Schema: public; Owner: james
--



--
-- TOC entry 4042 (class 0 OID 16880)
-- Dependencies: 245
-- Data for Name: query_templates; Type: TABLE DATA; Schema: public; Owner: james
--



--
-- TOC entry 4050 (class 0 OID 17206)
-- Dependencies: 253
-- Data for Name: service_agent_protocols; Type: TABLE DATA; Schema: public; Owner: ai_user
--



--
-- TOC entry 4019 (class 0 OID 16692)
-- Dependencies: 222
-- Data for Name: service_capability; Type: TABLE DATA; Schema: public; Owner: james
--

INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (7, 4, 'Retrieve customer profile and data by ID or email', 'retrieve_customer', '{}', '{}', '2025-06-12 16:11:29.386087');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (8, 4, 'Update customer information and preferences', 'update_customer', '{}', '{}', '2025-06-12 16:11:29.386091');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (9, 4, 'Search customers by various criteria', 'search_customers', '{}', '{}', '2025-06-12 16:11:29.386093');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (10, 4, 'Get customer analytics and insights', 'customer_analytics', '{}', '{}', '2025-06-12 16:11:29.386094');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (11, 5, 'Process payments via credit card, ACH, wire transfer', 'process_payment', '{}', '{}', '2025-06-12 16:11:29.392181');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (12, 5, 'Process refunds and chargebacks', 'refund_payment', '{}', '{}', '2025-06-12 16:11:29.392185');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (13, 5, 'Check payment status and history', 'payment_status', '{}', '{}', '2025-06-12 16:11:29.392187');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (14, 5, 'Generate payment reports and reconciliation', 'payment_reporting', '{}', '{}', '2025-06-12 16:11:29.392189');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (15, 6, 'Check real-time inventory levels across locations', 'check_inventory', '{}', '{}', '2025-06-12 16:11:29.394641');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (16, 6, 'Reserve inventory for orders and transfers', 'reserve_inventory', '{}', '{}', '2025-06-12 16:11:29.394644');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (17, 6, 'Update inventory counts and locations', 'update_inventory', '{}', '{}', '2025-06-12 16:11:29.394646');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (18, 6, 'Get inventory forecasts and recommendations', 'inventory_forecasting', '{}', '{}', '2025-06-12 16:11:29.394647');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (19, 7, 'Authenticate users with various methods (SSO, MFA)', 'authenticate_user', '{}', '{}', '2025-06-12 16:11:29.396975');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (20, 7, 'Check user permissions and roles', 'authorize_access', '{}', '{}', '2025-06-12 16:11:29.396979');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (21, 7, 'Create and manage user sessions', 'manage_sessions', '{}', '{}', '2025-06-12 16:11:29.396981');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (22, 7, 'Audit user access and authentication events', 'audit_access', '{}', '{}', '2025-06-12 16:11:29.396982');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (23, 8, 'Upload and store documents with metadata', 'upload_document', '{}', '{}', '2025-06-12 16:11:29.399482');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (24, 8, 'Retrieve documents by ID or search criteria', 'retrieve_document', '{}', '{}', '2025-06-12 16:11:29.399486');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (25, 8, 'Manage document versions and history', 'version_control', '{}', '{}', '2025-06-12 16:11:29.399488');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (26, 8, 'Full-text search across documents', 'document_search', '{}', '{}', '2025-06-12 16:11:29.399489');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (27, 9, 'Analyze campaign performance metrics in real-time', 'analyze_performance', '{}', '{}', '2025-06-12 16:11:29.401873');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (28, 9, 'Optimize audience targeting based on conversion data', 'optimize_targeting', '{}', '{}', '2025-06-12 16:11:29.401877');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (29, 9, 'Dynamically adjust campaign budgets for maximum ROI', 'adjust_budgets', '{}', '{}', '2025-06-12 16:11:29.401878');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (30, 9, 'Predict campaign outcomes and recommend changes', 'predict_outcomes', '{}', '{}', '2025-06-12 16:11:29.40188');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (31, 10, 'Create marketing content based on brand guidelines', 'generate_content', '{}', '{}', '2025-06-12 16:11:29.404105');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (32, 10, 'Personalize content for different audience segments', 'personalize_messages', '{}', '{}', '2025-06-12 16:11:29.404109');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (33, 10, 'A/B test and optimize marketing copy', 'optimize_copy', '{}', '{}', '2025-06-12 16:11:29.404111');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (34, 10, 'Schedule content across multiple channels', 'schedule_content', '{}', '{}', '2025-06-12 16:11:29.404112');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (35, 11, 'Calculate lead scores based on multiple factors', 'score_leads', '{}', '{}', '2025-06-12 16:11:29.406331');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (36, 11, 'Segment leads into qualification categories', 'segment_leads', '{}', '{}', '2025-06-12 16:11:29.406335');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (37, 11, 'Predict likelihood of lead conversion', 'predict_conversion', '{}', '{}', '2025-06-12 16:11:29.406336');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (38, 11, 'Route qualified leads to appropriate sales teams', 'route_leads', '{}', '{}', '2025-06-12 16:11:29.406337');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (39, 12, 'Track brand mentions across social platforms', 'monitor_mentions', '{}', '{}', '2025-06-12 16:11:29.408774');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (40, 12, 'Perform sentiment analysis on social conversations', 'analyze_sentiment', '{}', '{}', '2025-06-12 16:11:29.408778');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (41, 12, 'Identify and track key influencers', 'identify_influencers', '{}', '{}', '2025-06-12 16:11:29.40878');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (42, 12, 'Alert on potential PR issues or opportunities', 'alert_issues', '{}', '{}', '2025-06-12 16:11:29.408781');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (43, 13, 'Create and manage email audience segments', 'segment_audiences', '{}', '{}', '2025-06-12 16:11:29.411099');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (44, 13, 'Dynamically personalize email content', 'personalize_emails', '{}', '{}', '2025-06-12 16:11:29.411103');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (45, 13, 'Optimize email send times for engagement', 'optimize_timing', '{}', '{}', '2025-06-12 16:11:29.411105');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (46, 13, 'Track email metrics and generate reports', 'track_performance', '{}', '{}', '2025-06-12 16:11:29.411106');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (47, 14, 'Process and validate expense reports', 'process_expenses', '{}', '{}', '2025-06-12 16:11:29.413302');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (48, 14, 'Verify compliance with expense policies', 'check_compliance', '{}', '{}', '2025-06-12 16:11:29.413306');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (49, 14, 'Route expenses for appropriate approvals', 'route_approvals', '{}', '{}', '2025-06-12 16:11:29.413307');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (50, 14, 'Flag unusual or suspicious expenses', 'flag_anomalies', '{}', '{}', '2025-06-12 16:11:29.413309');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (51, 15, 'Extract data from invoices using OCR and AI', 'extract_data', '{}', '{}', '2025-06-12 16:11:29.415818');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (52, 15, 'Match invoices to purchase orders and receipts', 'match_orders', '{}', '{}', '2025-06-12 16:11:29.415821');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (53, 15, 'Validate invoice data and calculations', 'validate_invoices', '{}', '{}', '2025-06-12 16:11:29.415823');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (54, 15, 'Route approved invoices for payment', 'route_payment', '{}', '{}', '2025-06-12 16:11:29.415824');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (55, 16, 'Monitor real-time spending against budgets', 'track_spending', '{}', '{}', '2025-06-12 16:11:29.418123');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (56, 16, 'Forecast budget utilization and overruns', 'forecast_budgets', '{}', '{}', '2025-06-12 16:11:29.418126');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (57, 16, 'Alert on significant budget variances', 'alert_variances', '{}', '{}', '2025-06-12 16:11:29.418128');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (58, 16, 'Generate budget performance reports', 'generate_reports', '{}', '{}', '2025-06-12 16:11:29.418129');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (59, 17, 'Calculate taxes for various jurisdictions', 'calculate_taxes', '{}', '{}', '2025-06-12 16:11:29.420324');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (60, 17, 'Prepare tax returns and filings', 'prepare_filings', '{}', '{}', '2025-06-12 16:11:29.420328');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (61, 17, 'Track and alert on tax deadlines', 'track_deadlines', '{}', '{}', '2025-06-12 16:11:29.420329');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (62, 17, 'Audit transactions for tax compliance', 'audit_compliance', '{}', '{}', '2025-06-12 16:11:29.42033');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (63, 18, 'Predict future cash flows based on patterns', 'forecast_cashflow', '{}', '{}', '2025-06-12 16:11:29.422525');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (64, 18, 'Recommend working capital optimizations', 'optimize_working_capital', '{}', '{}', '2025-06-12 16:11:29.422529');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (65, 18, 'Run what-if scenarios for cash planning', 'scenario_analysis', '{}', '{}', '2025-06-12 16:11:29.42253');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (66, 18, 'Alert on potential cash shortfalls', 'alert_shortfalls', '{}', '{}', '2025-06-12 16:11:29.422531');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (67, 19, 'Real-time transaction monitoring and analysis', 'monitor_transactions', '{}', '{}', '2025-06-12 16:11:29.424982');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (68, 19, 'Detect anomalous patterns and behaviors', 'detect_anomalies', '{}', '{}', '2025-06-12 16:11:29.424986');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (69, 19, 'Score transactions and entities for fraud risk', 'risk_scoring', '{}', '{}', '2025-06-12 16:11:29.424987');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (70, 19, 'Alert security team on high-risk activities', 'alert_security', '{}', '{}', '2025-06-12 16:11:29.424988');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (71, 20, 'Monitor competitor activities and strategies', 'track_competitors', '{}', '{}', '2025-06-12 16:11:29.427572');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (72, 20, 'Identify and analyze market trends', 'analyze_trends', '{}', '{}', '2025-06-12 16:11:29.427575');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (73, 20, 'Forecast market conditions and opportunities', 'forecast_market', '{}', '{}', '2025-06-12 16:11:29.427577');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (74, 20, 'Generate actionable market insights', 'generate_insights', '{}', '{}', '2025-06-12 16:11:29.427578');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (75, 21, 'Monitor and track key performance indicators', 'track_kpis', '{}', '{}', '2025-06-12 16:11:29.431014');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (76, 21, 'Analyze business metrics and performance', 'analyze_metrics', '{}', '{}', '2025-06-12 16:11:29.431018');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (77, 21, 'Generate executive dashboards', 'create_dashboards', '{}', '{}', '2025-06-12 16:11:29.431019');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (78, 21, 'Identify performance trends and patterns', 'identify_trends', '{}', '{}', '2025-06-12 16:11:29.43102');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (79, 22, 'Analyze customer behavior patterns', 'analyze_behavior', '{}', '{}', '2025-06-12 16:11:29.433271');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (80, 22, 'Create customer segments and personas', 'segment_customers', '{}', '{}', '2025-06-12 16:11:29.433275');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (81, 22, 'Predict customer churn probability', 'predict_churn', '{}', '{}', '2025-06-12 16:11:29.433276');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (82, 22, 'Recommend retention and growth actions', 'recommend_actions', '{}', '{}', '2025-06-12 16:11:29.433277');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (83, 23, 'Analyze current pricing effectiveness', 'analyze_pricing', '{}', '{}', '2025-06-12 16:11:29.435623');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (84, 23, 'Recommend optimal pricing strategies', 'optimize_prices', '{}', '{}', '2025-06-12 16:11:29.435627');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (85, 23, 'Monitor competitor pricing in real-time', 'monitor_competition', '{}', '{}', '2025-06-12 16:11:29.435629');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (86, 23, 'Forecast revenue impact of price changes', 'forecast_impact', '{}', '{}', '2025-06-12 16:11:29.43563');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (87, 24, 'Automatically map business processes from logs', 'map_processes', '{}', '{}', '2025-06-12 16:11:29.437905');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (88, 24, 'Identify process bottlenecks and delays', 'identify_bottlenecks', '{}', '{}', '2025-06-12 16:11:29.437908');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (89, 24, 'Recommend process optimizations', 'recommend_improvements', '{}', '{}', '2025-06-12 16:11:29.43791');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (90, 24, 'Measure process efficiency and compliance', 'measure_efficiency', '{}', '{}', '2025-06-12 16:11:29.437911');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (91, 25, 'Validate data against quality rules', 'validate_data', '{}', '{}', '2025-06-12 16:11:29.440142');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (92, 25, 'Clean and standardize data', 'cleanse_data', '{}', '{}', '2025-06-12 16:11:29.440145');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (93, 25, 'Enrich data with external sources', 'enrich_data', '{}', '{}', '2025-06-12 16:11:29.440147');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (94, 25, 'Monitor data quality metrics', 'monitor_quality', '{}', '{}', '2025-06-12 16:11:29.440148');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (95, 26, 'Schedule and manage ETL pipelines', 'schedule_pipelines', '{}', '{}', '2025-06-12 16:11:29.442733');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (96, 26, 'Transform data between formats and schemas', 'transform_data', '{}', '{}', '2025-06-12 16:11:29.442737');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (97, 26, 'Monitor ETL job execution and performance', 'monitor_jobs', '{}', '{}', '2025-06-12 16:11:29.442739');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (98, 26, 'Handle errors and retry failed jobs', 'handle_errors', '{}', '{}', '2025-06-12 16:11:29.442741');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (99, 27, 'Archive data based on retention policies', 'archive_data', '{}', '{}', '2025-06-12 16:11:29.445123');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (100, 27, 'Compress and optimize storage usage', 'compress_storage', '{}', '{}', '2025-06-12 16:11:29.445127');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (101, 27, 'Manage data lifecycle and retention', 'manage_lifecycle', '{}', '{}', '2025-06-12 16:11:29.445128');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (102, 27, 'Restore archived data on demand', 'restore_data', '{}', '{}', '2025-06-12 16:11:29.44513');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (103, 28, 'Process real-time data streams', 'process_streams', '{}', '{}', '2025-06-12 16:11:29.447461');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (104, 28, 'Detect patterns and events in streams', 'detect_events', '{}', '{}', '2025-06-12 16:11:29.447465');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (105, 28, 'Aggregate streaming metrics in real-time', 'aggregate_metrics', '{}', '{}', '2025-06-12 16:11:29.447467');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (106, 28, 'Trigger actions based on stream events', 'trigger_actions', '{}', '{}', '2025-06-12 16:11:29.447468');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (107, 29, 'Catalog data assets and metadata', 'catalog_assets', '{}', '{}', '2025-06-12 16:11:29.449975');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (108, 29, 'Track data lineage and dependencies', 'track_lineage', '{}', '{}', '2025-06-12 16:11:29.449979');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (109, 29, 'Enable data discovery and search', 'enable_discovery', '{}', '{}', '2025-06-12 16:11:29.44998');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (110, 29, 'Manage business glossary and definitions', 'manage_glossary', '{}', '{}', '2025-06-12 16:11:29.449982');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (111, 30, 'Screen and rank resumes using AI', 'screen_resumes', '{}', '{}', '2025-06-12 16:11:29.452524');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (112, 30, 'Match candidates to job requirements', 'match_candidates', '{}', '{}', '2025-06-12 16:11:29.452528');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (113, 30, 'Coordinate and schedule interviews', 'schedule_interviews', '{}', '{}', '2025-06-12 16:11:29.452529');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (114, 30, 'Track recruitment pipeline and metrics', 'track_pipeline', '{}', '{}', '2025-06-12 16:11:29.45253');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (115, 31, 'Create accounts and provision access', 'create_accounts', '{}', '{}', '2025-06-12 16:11:29.454977');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (116, 31, 'Assign onboarding tasks and training', 'assign_tasks', '{}', '{}', '2025-06-12 16:11:29.454981');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (117, 31, 'Track onboarding progress and completion', 'track_progress', '{}', '{}', '2025-06-12 16:11:29.454983');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (118, 31, 'Collect and verify required documents', 'collect_documents', '{}', '{}', '2025-06-12 16:11:29.454984');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (119, 32, 'Optimize space allocation and usage', 'manage_space', '{}', '{}', '2025-06-12 16:11:29.457186');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (120, 32, 'Schedule preventive maintenance', 'schedule_maintenance', '{}', '{}', '2025-06-12 16:11:29.45719');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (121, 32, 'Track facility assets and equipment', 'track_assets', '{}', '{}', '2025-06-12 16:11:29.457191');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (122, 32, 'Process facility service requests', 'handle_requests', '{}', '{}', '2025-06-12 16:11:29.457192');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (123, 33, 'Monitor compliance with regulations', 'monitor_compliance', '{}', '{}', '2025-06-12 16:11:29.458909');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (124, 33, 'Track policy adherence and violations', 'track_policies', '{}', '{}', '2025-06-12 16:11:29.458913');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (125, 33, 'Prepare documentation for audits', 'prepare_audits', '{}', '{}', '2025-06-12 16:11:29.458914');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (126, 33, 'Assess compliance risks and gaps', 'assess_risks', '{}', '{}', '2025-06-12 16:11:29.458916');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (127, 34, 'Generate detailed sales reports with custom date ranges and filters', 'Sales Report Generation', 'null', 'null', '2025-06-12 21:35:30.756647');
INSERT INTO public.service_capability (id, service_id, capability_desc, capability_name, input_schema, output_schema, created_at) VALUES (128, 34, 'Analyze revenue trends, forecasts, and performance metrics', 'Revenue Analysis', 'null', 'null', '2025-06-12 21:35:30.845222');


--
-- TOC entry 4038 (class 0 OID 16844)
-- Dependencies: 241
-- Data for Name: service_health; Type: TABLE DATA; Schema: public; Owner: james
--



--
-- TOC entry 4052 (class 0 OID 17227)
-- Dependencies: 255
-- Data for Name: service_industries; Type: TABLE DATA; Schema: public; Owner: ai_user
--



--
-- TOC entry 4023 (class 0 OID 16722)
-- Dependencies: 226
-- Data for Name: service_industry; Type: TABLE DATA; Schema: public; Owner: james
--

INSERT INTO public.service_industry (id, service_id, domain) VALUES (7, 4, 'Customer Service');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (8, 4, 'Data Management');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (9, 4, 'Analytics');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (10, 5, 'Finance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (11, 5, 'E-commerce');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (12, 5, 'Compliance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (13, 6, 'Supply Chain');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (14, 6, 'Operations');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (15, 6, 'Retail');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (16, 7, 'Security');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (17, 7, 'IT Infrastructure');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (18, 7, 'Compliance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (19, 8, 'Document Management');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (20, 8, 'Compliance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (21, 8, 'Knowledge Management');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (22, 9, 'Marketing');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (23, 9, 'Analytics');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (24, 9, 'Automation');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (25, 10, 'Marketing');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (26, 10, 'Content Management');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (27, 10, 'Social Media');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (28, 11, 'Marketing');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (29, 11, 'Sales');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (30, 11, 'Analytics');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (31, 12, 'Marketing');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (32, 12, 'Social Media');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (33, 12, 'Customer Service');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (34, 13, 'Marketing');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (35, 13, 'Communications');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (36, 13, 'Analytics');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (37, 14, 'Finance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (38, 14, 'Compliance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (39, 14, 'Operations');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (40, 15, 'Finance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (41, 15, 'Accounts Payable');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (42, 15, 'Automation');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (43, 16, 'Finance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (44, 16, 'Planning');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (45, 16, 'Analytics');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (46, 17, 'Finance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (47, 17, 'Compliance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (48, 17, 'Legal');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (49, 18, 'Finance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (50, 18, 'Treasury');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (51, 18, 'Analytics');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (52, 19, 'Finance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (53, 19, 'Security');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (54, 19, 'Risk Management');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (55, 20, 'Business Intelligence');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (56, 20, 'Strategy');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (57, 20, 'Analytics');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (58, 21, 'Business Intelligence');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (59, 21, 'Analytics');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (60, 21, 'Reporting');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (61, 22, 'Business Intelligence');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (62, 22, 'Customer Analytics');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (63, 22, 'Marketing');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (64, 23, 'Business Intelligence');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (65, 23, 'Revenue Management');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (66, 23, 'Analytics');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (67, 24, 'Business Intelligence');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (68, 24, 'Operations');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (69, 24, 'Process Improvement');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (70, 25, 'Data Management');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (71, 25, 'Quality Assurance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (72, 25, 'Analytics');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (73, 26, 'Data Management');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (74, 26, 'Integration');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (75, 26, 'Automation');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (76, 27, 'Data Management');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (77, 27, 'Storage');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (78, 27, 'Compliance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (79, 28, 'Data Management');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (80, 28, 'Real-time Analytics');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (81, 28, 'Event Processing');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (82, 29, 'Data Management');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (83, 29, 'Governance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (84, 29, 'Discovery');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (85, 30, 'Human Resources');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (86, 30, 'Recruitment');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (87, 30, 'Automation');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (88, 31, 'Human Resources');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (89, 31, 'Operations');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (90, 31, 'Compliance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (91, 32, 'Operations');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (92, 32, 'Facilities');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (93, 32, 'Asset Management');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (94, 33, 'Compliance');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (95, 33, 'Risk Management');
INSERT INTO public.service_industry (id, service_id, domain) VALUES (96, 33, 'Legal');


--
-- TOC entry 4048 (class 0 OID 17186)
-- Dependencies: 251
-- Data for Name: service_integration_details; Type: TABLE DATA; Schema: public; Owner: ai_user
--

INSERT INTO public.service_integration_details (id, service_id, access_protocol, base_endpoint, auth_method, auth_config, auth_endpoint, rate_limit_requests, rate_limit_window_seconds, max_concurrent_requests, circuit_breaker_config, default_headers, request_content_type, response_content_type, request_transform, response_transform, esb_type, esb_service_name, esb_routing_key, esb_operation, esb_adapter_type, esb_namespace, esb_version, health_check_endpoint, health_check_interval_seconds, created_at, updated_at) VALUES (1, 4, 'https', 'https://api.enterprise.com/customers/v2', 'None', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'application/json', 'application/json', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-06-13 09:26:47.636416', '2025-06-13 09:26:47.636416');
INSERT INTO public.service_integration_details (id, service_id, access_protocol, base_endpoint, auth_method, auth_config, auth_endpoint, rate_limit_requests, rate_limit_window_seconds, max_concurrent_requests, circuit_breaker_config, default_headers, request_content_type, response_content_type, request_transform, response_transform, esb_type, esb_service_name, esb_routing_key, esb_operation, esb_adapter_type, esb_namespace, esb_version, health_check_endpoint, health_check_interval_seconds, created_at, updated_at) VALUES (2, 5, 'https', 'https://api.enterprise.com/payments/v3', 'None', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'application/json', 'application/json', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-06-13 09:26:47.636416', '2025-06-13 09:26:47.636416');
INSERT INTO public.service_integration_details (id, service_id, access_protocol, base_endpoint, auth_method, auth_config, auth_endpoint, rate_limit_requests, rate_limit_window_seconds, max_concurrent_requests, circuit_breaker_config, default_headers, request_content_type, response_content_type, request_transform, response_transform, esb_type, esb_service_name, esb_routing_key, esb_operation, esb_adapter_type, esb_namespace, esb_version, health_check_endpoint, health_check_interval_seconds, created_at, updated_at) VALUES (3, 6, 'https', 'https://api.enterprise.com/inventory/v1', 'None', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'application/json', 'application/json', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-06-13 09:26:47.636416', '2025-06-13 09:26:47.636416');
INSERT INTO public.service_integration_details (id, service_id, access_protocol, base_endpoint, auth_method, auth_config, auth_endpoint, rate_limit_requests, rate_limit_window_seconds, max_concurrent_requests, circuit_breaker_config, default_headers, request_content_type, response_content_type, request_transform, response_transform, esb_type, esb_service_name, esb_routing_key, esb_operation, esb_adapter_type, esb_namespace, esb_version, health_check_endpoint, health_check_interval_seconds, created_at, updated_at) VALUES (4, 7, 'https', 'https://api.enterprise.com/auth/v4', 'None', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'application/json', 'application/json', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-06-13 09:26:47.636416', '2025-06-13 09:26:47.636416');
INSERT INTO public.service_integration_details (id, service_id, access_protocol, base_endpoint, auth_method, auth_config, auth_endpoint, rate_limit_requests, rate_limit_window_seconds, max_concurrent_requests, circuit_breaker_config, default_headers, request_content_type, response_content_type, request_transform, response_transform, esb_type, esb_service_name, esb_routing_key, esb_operation, esb_adapter_type, esb_namespace, esb_version, health_check_endpoint, health_check_interval_seconds, created_at, updated_at) VALUES (5, 8, 'https', 'https://api.enterprise.com/documents/v2', 'None', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'application/json', 'application/json', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-06-13 09:26:47.636416', '2025-06-13 09:26:47.636416');
INSERT INTO public.service_integration_details (id, service_id, access_protocol, base_endpoint, auth_method, auth_config, auth_endpoint, rate_limit_requests, rate_limit_window_seconds, max_concurrent_requests, circuit_breaker_config, default_headers, request_content_type, response_content_type, request_transform, response_transform, esb_type, esb_service_name, esb_routing_key, esb_operation, esb_adapter_type, esb_namespace, esb_version, health_check_endpoint, health_check_interval_seconds, created_at, updated_at) VALUES (6, 34, 'https', 'https://api.kpath.ai/sales-analytics', 'None', NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'application/json', 'application/json', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-06-13 09:26:47.636416', '2025-06-13 09:26:47.636416');
INSERT INTO public.service_integration_details (id, service_id, access_protocol, base_endpoint, auth_method, auth_config, auth_endpoint, rate_limit_requests, rate_limit_window_seconds, max_concurrent_requests, circuit_breaker_config, default_headers, request_content_type, response_content_type, request_transform, response_transform, esb_type, esb_service_name, esb_routing_key, esb_operation, esb_adapter_type, esb_namespace, esb_version, health_check_endpoint, health_check_interval_seconds, created_at, updated_at) VALUES (7, 35, 'https', 'https://esb.company.com/mulesoft/api', 'Custom', '{"type": "mulesoft_token", "token_header": "X-Mule-Token"}', NULL, 10, 60, NULL, NULL, NULL, 'text/xml', 'text/xml', NULL, NULL, 'MuleSoft', 'sap-finance-connector', 'finance.sap.v1', 'FinanceDataRetrieval', 'SAP', NULL, NULL, NULL, NULL, '2025-06-13 09:27:55.560324', '2025-06-13 09:27:55.560324');
INSERT INTO public.service_integration_details (id, service_id, access_protocol, base_endpoint, auth_method, auth_config, auth_endpoint, rate_limit_requests, rate_limit_window_seconds, max_concurrent_requests, circuit_breaker_config, default_headers, request_content_type, response_content_type, request_transform, response_transform, esb_type, esb_service_name, esb_routing_key, esb_operation, esb_adapter_type, esb_namespace, esb_version, health_check_endpoint, health_check_interval_seconds, created_at, updated_at) VALUES (8, 36, 'https', 'https://api.openai.com/v1', 'APIKey', '{"header_name": "Authorization", "header_prefix": "Bearer"}', NULL, 50, 60, NULL, '{"failure_threshold": 5, "recovery_timeout_ms": 30000, "expected_error_codes": [429, 503]}', NULL, 'application/json', 'application/json', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '2025-06-13 09:28:15.843794', '2025-06-13 09:28:15.843794');


--
-- TOC entry 4036 (class 0 OID 16825)
-- Dependencies: 239
-- Data for Name: service_versions; Type: TABLE DATA; Schema: public; Owner: james
--



--
-- TOC entry 4017 (class 0 OID 16677)
-- Dependencies: 220
-- Data for Name: services; Type: TABLE DATA; Schema: public; Owner: james
--

INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (4, 'CustomerDataAPI', 'Core API for accessing and managing customer master data, profiles, and preferences across the enterprise', 'https://api.enterprise.com/customers/v2', '2.3.0', 'active', '2025-06-12 16:11:29.381883', '2025-06-13 09:26:40.434707', 'API', '{REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (5, 'PaymentGatewayAPI', 'Enterprise payment processing API supporting multiple payment methods, currencies, and compliance standards', 'https://api.enterprise.com/payments/v3', '3.1.0', 'active', '2025-06-12 16:11:29.384079', '2025-06-13 09:26:40.434707', 'API', '{REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (6, 'InventoryManagementAPI', 'Real-time inventory tracking and management API for warehouses, stores, and distribution centers', 'https://api.enterprise.com/inventory/v1', '1.8.0', 'active', '2025-06-12 16:11:29.391699', '2025-06-13 09:26:40.434707', 'API', '{REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (7, 'AuthenticationAPI', 'Enterprise-wide authentication and authorization API with SSO, MFA, and role-based access control', 'https://api.enterprise.com/auth/v4', '4.0.0', 'active', '2025-06-12 16:11:29.394215', '2025-06-13 09:26:40.434707', 'API', '{REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (8, 'DocumentStorageAPI', 'Enterprise document management API for storing, retrieving, and managing business documents with versioning', 'https://api.enterprise.com/documents/v2', '2.5.0', 'active', '2025-06-12 16:11:29.396456', '2025-06-13 09:26:40.434707', 'API', '{REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (9, 'CampaignOptimizationAgent', 'AI-powered agent that continuously optimizes marketing campaigns based on performance metrics and ROI', NULL, '1.2.0', 'active', '2025-06-12 16:11:29.39899', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (10, 'ContentGenerationAgent', 'Automated content creation agent for marketing materials, social media posts, and email campaigns', NULL, '2.0.0', 'active', '2025-06-12 16:11:29.401432', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (11, 'LeadScoringAgent', 'Machine learning agent that scores and qualifies leads based on behavior, demographics, and engagement', NULL, '1.5.0', 'active', '2025-06-12 16:11:29.403683', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (12, 'SocialMediaMonitoringAgent', 'Monitors social media channels for brand mentions, sentiment analysis, and engagement opportunities', NULL, '1.8.0', 'active', '2025-06-12 16:11:29.405908', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (13, 'EmailMarketingAgent', 'Automated email marketing agent for campaign execution, personalization, and performance tracking', NULL, '2.2.0', 'active', '2025-06-12 16:11:29.408235', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (14, 'ExpenseApprovalAgent', 'Automated expense report processing and approval agent with policy compliance checking', NULL, '1.6.0', 'active', '2025-06-12 16:11:29.410671', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (15, 'InvoiceProcessingAgent', 'Intelligent agent for processing, matching, and routing invoices through the AP workflow', NULL, '2.1.0', 'active', '2025-06-12 16:11:29.41288', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (16, 'BudgetMonitoringAgent', 'Real-time budget monitoring agent that tracks spending, forecasts overruns, and alerts stakeholders', NULL, '1.4.0', 'active', '2025-06-12 16:11:29.415315', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (17, 'TaxComplianceAgent', 'Automated tax calculation, filing, and compliance agent for multiple jurisdictions', NULL, '3.0.0', 'active', '2025-06-12 16:11:29.417697', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (18, 'CashFlowForecastingAgent', 'Predictive analytics agent for cash flow forecasting and working capital optimization', NULL, '1.9.0', 'active', '2025-06-12 16:11:29.419916', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (19, 'FraudDetectionAgent', 'AI-powered fraud detection agent monitoring transactions and identifying suspicious patterns', NULL, '2.5.0', 'active', '2025-06-12 16:11:29.422112', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (20, 'MarketIntelligenceAgent', 'Gathers and analyzes market data, competitor information, and industry trends for strategic planning', NULL, '1.7.0', 'active', '2025-06-12 16:11:29.424378', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (21, 'PerformanceAnalyticsAgent', 'Analyzes business performance metrics, KPIs, and generates executive dashboards and reports', NULL, '2.3.0', 'active', '2025-06-12 16:11:29.42709', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (22, 'CustomerInsightsAgent', 'Analyzes customer behavior, preferences, and journey to provide actionable business insights', NULL, '1.8.0', 'active', '2025-06-12 16:11:29.430561', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (23, 'PricingOptimizationAgent', 'Dynamic pricing agent that optimizes prices based on demand, competition, and profitability targets', NULL, '1.5.0', 'active', '2025-06-12 16:11:29.432838', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (24, 'ProcessMiningAgent', 'Analyzes business processes to identify bottlenecks, inefficiencies, and optimization opportunities', NULL, '1.3.0', 'active', '2025-06-12 16:11:29.435175', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (25, 'DataQualityAgent', 'Monitors and improves data quality across enterprise systems through validation, cleansing, and enrichment', NULL, '2.0.0', 'active', '2025-06-12 16:11:29.437477', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (26, 'ETLOrchestrationAgent', 'Orchestrates complex ETL/ELT pipelines for data integration across multiple systems and formats', NULL, '3.1.0', 'active', '2025-06-12 16:11:29.439702', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (27, 'DataArchivingAgent', 'Manages data lifecycle, archiving, and retention policies across enterprise data stores', NULL, '1.6.0', 'active', '2025-06-12 16:11:29.44212', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (28, 'RealtimeStreamProcessorAgent', 'Processes real-time data streams for analytics, alerting, and event-driven architectures', NULL, '2.2.0', 'active', '2025-06-12 16:11:29.444691', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (29, 'DataCatalogAgent', 'Maintains enterprise data catalog with metadata, lineage, and discovery capabilities', NULL, '1.9.0', 'active', '2025-06-12 16:11:29.446996', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (30, 'RecruitmentAutomationAgent', 'Automates recruitment processes including resume screening, candidate matching, and interview scheduling', NULL, '1.7.0', 'active', '2025-06-12 16:11:29.449399', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (31, 'EmployeeOnboardingAgent', 'Manages employee onboarding workflows, documentation, and task assignments for new hires', NULL, '1.4.0', 'active', '2025-06-12 16:11:29.452042', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (32, 'FacilityManagementAgent', 'Manages facility operations including space allocation, maintenance scheduling, and resource optimization', NULL, '1.8.0', 'active', '2025-06-12 16:11:29.454521', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (33, 'ComplianceMonitoringAgent', 'Monitors regulatory compliance, tracks policy adherence, and manages audit preparations', NULL, '2.1.0', 'active', '2025-06-12 16:11:29.456771', '2025-06-13 09:26:40.434707', 'InternalAgent', '{AgentMessage,REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (34, 'Sales Analytics Service', 'Provides comprehensive sales data analysis, reporting, and visualization capabilities', 'https://api.kpath.ai/sales-analytics', '2.1.0', 'active', '2025-06-12 21:35:30.727754', '2025-06-13 09:26:40.434707', 'MicroService', '{REST}', 'internal', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (35, 'SAPFinanceConnector', 'Access SAP financial data through MuleSoft ESB for real-time balance queries and transaction history', NULL, '1.0.0', 'active', '2025-06-13 09:27:46.664199', '2025-06-13 09:27:46.664199', 'ESBEndpoint', '{ESB,SOAP}', 'restricted', NULL, NULL, NULL, 30000, NULL);
INSERT INTO public.services (id, name, description, endpoint, version, status, created_at, updated_at, tool_type, interaction_modes, visibility, deprecation_date, deprecation_notice, success_criteria, default_timeout_ms, default_retry_policy) VALUES (36, 'OpenAIAssistant', 'External AI assistant for natural language processing, text generation, and analysis tasks', NULL, NULL, 'active', '2025-06-13 09:28:01.210533', '2025-06-13 09:28:01.210533', 'ExternalAgent', '{REST,Webhook}', 'restricted', NULL, NULL, NULL, 60000, NULL);


--
-- TOC entry 4046 (class 0 OID 16911)
-- Dependencies: 249
-- Data for Name: user_selections; Type: TABLE DATA; Schema: public; Owner: james
--



--
-- TOC entry 4025 (class 0 OID 16738)
-- Dependencies: 228
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: james
--

INSERT INTO public.users (id, email, role, org_id, attributes, created_at, updated_at, password_hash, is_active, username) VALUES (3, 'admin@kpath.ai', 'admin', NULL, '{"department": "IT", "full_access": true}', '2025-06-12 20:49:32.096363', '2025-06-12 20:49:32.096369', '$2b$12$C0IIXA1NlBDyCPTwGx4.oeHXrFaSYJFwVhEPkxI6j4/E9sCIfBAg6', true, NULL);


--
-- TOC entry 4083 (class 0 OID 0)
-- Dependencies: 229
-- Name: access_policy_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.access_policy_id_seq', 1, false);


--
-- TOC entry 4084 (class 0 OID 0)
-- Dependencies: 242
-- Name: api_keys_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.api_keys_id_seq', 1, false);


--
-- TOC entry 4085 (class 0 OID 0)
-- Dependencies: 233
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 1, false);


--
-- TOC entry 4086 (class 0 OID 0)
-- Dependencies: 231
-- Name: faiss_index_metadata_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.faiss_index_metadata_id_seq', 1, false);


--
-- TOC entry 4087 (class 0 OID 0)
-- Dependencies: 235
-- Name: feedback_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.feedback_log_id_seq', 1, false);


--
-- TOC entry 4088 (class 0 OID 0)
-- Dependencies: 246
-- Name: integration_configs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.integration_configs_id_seq', 1, false);


--
-- TOC entry 4089 (class 0 OID 0)
-- Dependencies: 223
-- Name: interaction_capability_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.interaction_capability_id_seq', 1, false);


--
-- TOC entry 4090 (class 0 OID 0)
-- Dependencies: 244
-- Name: query_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.query_templates_id_seq', 1, false);


--
-- TOC entry 4091 (class 0 OID 0)
-- Dependencies: 252
-- Name: service_agent_protocols_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ai_user
--

SELECT pg_catalog.setval('public.service_agent_protocols_id_seq', 1, true);


--
-- TOC entry 4092 (class 0 OID 0)
-- Dependencies: 221
-- Name: service_capability_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.service_capability_id_seq', 128, true);


--
-- TOC entry 4093 (class 0 OID 0)
-- Dependencies: 240
-- Name: service_health_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.service_health_id_seq', 1, false);


--
-- TOC entry 4094 (class 0 OID 0)
-- Dependencies: 254
-- Name: service_industries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ai_user
--

SELECT pg_catalog.setval('public.service_industries_id_seq', 1, false);


--
-- TOC entry 4095 (class 0 OID 0)
-- Dependencies: 225
-- Name: service_industry_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.service_industry_id_seq', 96, true);


--
-- TOC entry 4096 (class 0 OID 0)
-- Dependencies: 250
-- Name: service_integration_details_id_seq; Type: SEQUENCE SET; Schema: public; Owner: ai_user
--

SELECT pg_catalog.setval('public.service_integration_details_id_seq', 9, true);


--
-- TOC entry 4097 (class 0 OID 0)
-- Dependencies: 238
-- Name: service_versions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.service_versions_id_seq', 1, false);


--
-- TOC entry 4098 (class 0 OID 0)
-- Dependencies: 219
-- Name: services_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.services_id_seq', 37, true);


--
-- TOC entry 4099 (class 0 OID 0)
-- Dependencies: 248
-- Name: user_selections_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.user_selections_id_seq', 1, false);


--
-- TOC entry 4100 (class 0 OID 0)
-- Dependencies: 227
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: james
--

SELECT pg_catalog.setval('public.users_id_seq', 3, true);


--
-- TOC entry 3797 (class 2606 OID 16763)
-- Name: access_policy access_policy_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.access_policy
    ADD CONSTRAINT access_policy_pkey PRIMARY KEY (id);


--
-- TOC entry 3823 (class 2606 OID 16873)
-- Name: api_keys api_keys_key_hash_key; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_key_hash_key UNIQUE (key_hash);


--
-- TOC entry 3825 (class 2606 OID 16871)
-- Name: api_keys api_keys_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_pkey PRIMARY KEY (id);


--
-- TOC entry 3801 (class 2606 OID 16788)
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 3812 (class 2606 OID 16823)
-- Name: cache_entries cache_entries_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.cache_entries
    ADD CONSTRAINT cache_entries_pkey PRIMARY KEY (key);


--
-- TOC entry 3799 (class 2606 OID 16778)
-- Name: faiss_index_metadata faiss_index_metadata_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.faiss_index_metadata
    ADD CONSTRAINT faiss_index_metadata_pkey PRIMARY KEY (id);


--
-- TOC entry 3806 (class 2606 OID 16804)
-- Name: feedback_log feedback_log_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.feedback_log
    ADD CONSTRAINT feedback_log_pkey PRIMARY KEY (id);


--
-- TOC entry 3833 (class 2606 OID 16907)
-- Name: integration_configs integration_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.integration_configs
    ADD CONSTRAINT integration_configs_pkey PRIMARY KEY (id);


--
-- TOC entry 3835 (class 2606 OID 16909)
-- Name: integration_configs integration_configs_type_name_key; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.integration_configs
    ADD CONSTRAINT integration_configs_type_name_key UNIQUE (type, name);


--
-- TOC entry 3783 (class 2606 OID 16715)
-- Name: interaction_capability interaction_capability_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.interaction_capability
    ADD CONSTRAINT interaction_capability_pkey PRIMARY KEY (id);


--
-- TOC entry 3829 (class 2606 OID 16891)
-- Name: query_templates query_templates_name_key; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.query_templates
    ADD CONSTRAINT query_templates_name_key UNIQUE (name);


--
-- TOC entry 3831 (class 2606 OID 16889)
-- Name: query_templates query_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.query_templates
    ADD CONSTRAINT query_templates_pkey PRIMARY KEY (id);


--
-- TOC entry 3846 (class 2606 OID 17218)
-- Name: service_agent_protocols service_agent_protocols_pkey; Type: CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.service_agent_protocols
    ADD CONSTRAINT service_agent_protocols_pkey PRIMARY KEY (id);


--
-- TOC entry 3848 (class 2606 OID 17220)
-- Name: service_agent_protocols service_agent_protocols_service_id_key; Type: CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.service_agent_protocols
    ADD CONSTRAINT service_agent_protocols_service_id_key UNIQUE (service_id);


--
-- TOC entry 3779 (class 2606 OID 16700)
-- Name: service_capability service_capability_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.service_capability
    ADD CONSTRAINT service_capability_pkey PRIMARY KEY (id);


--
-- TOC entry 3821 (class 2606 OID 16855)
-- Name: service_health service_health_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.service_health
    ADD CONSTRAINT service_health_pkey PRIMARY KEY (id);


--
-- TOC entry 3850 (class 2606 OID 17235)
-- Name: service_industries service_industries_pkey; Type: CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.service_industries
    ADD CONSTRAINT service_industries_pkey PRIMARY KEY (id);


--
-- TOC entry 3852 (class 2606 OID 17237)
-- Name: service_industries service_industries_service_id_industry_key; Type: CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.service_industries
    ADD CONSTRAINT service_industries_service_id_industry_key UNIQUE (service_id, industry);


--
-- TOC entry 3787 (class 2606 OID 16729)
-- Name: service_industry service_industry_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.service_industry
    ADD CONSTRAINT service_industry_pkey PRIMARY KEY (id);


--
-- TOC entry 3789 (class 2606 OID 16731)
-- Name: service_industry service_industry_service_id_domain_key; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.service_industry
    ADD CONSTRAINT service_industry_service_id_domain_key UNIQUE (service_id, domain);


--
-- TOC entry 3842 (class 2606 OID 17197)
-- Name: service_integration_details service_integration_details_pkey; Type: CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.service_integration_details
    ADD CONSTRAINT service_integration_details_pkey PRIMARY KEY (id);


--
-- TOC entry 3844 (class 2606 OID 17199)
-- Name: service_integration_details service_integration_details_service_id_key; Type: CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.service_integration_details
    ADD CONSTRAINT service_integration_details_service_id_key UNIQUE (service_id);


--
-- TOC entry 3817 (class 2606 OID 16835)
-- Name: service_versions service_versions_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.service_versions
    ADD CONSTRAINT service_versions_pkey PRIMARY KEY (id);


--
-- TOC entry 3819 (class 2606 OID 16837)
-- Name: service_versions service_versions_service_id_version_key; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.service_versions
    ADD CONSTRAINT service_versions_service_id_version_key UNIQUE (service_id, version);


--
-- TOC entry 3773 (class 2606 OID 16690)
-- Name: services services_name_key; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_name_key UNIQUE (name);


--
-- TOC entry 3775 (class 2606 OID 16688)
-- Name: services services_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.services
    ADD CONSTRAINT services_pkey PRIMARY KEY (id);


--
-- TOC entry 3840 (class 2606 OID 16920)
-- Name: user_selections user_selections_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.user_selections
    ADD CONSTRAINT user_selections_pkey PRIMARY KEY (id);


--
-- TOC entry 3791 (class 2606 OID 16751)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 3793 (class 2606 OID 16749)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 3795 (class 2606 OID 17249)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 3826 (class 1259 OID 16949)
-- Name: idx_api_keys_hash; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_api_keys_hash ON public.api_keys USING btree (key_hash);


--
-- TOC entry 3827 (class 1259 OID 16948)
-- Name: idx_api_keys_user; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_api_keys_user ON public.api_keys USING btree (user_id);


--
-- TOC entry 3802 (class 1259 OID 16941)
-- Name: idx_audit_action; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_audit_action ON public.audit_logs USING btree (action);


--
-- TOC entry 3803 (class 1259 OID 16939)
-- Name: idx_audit_timestamp; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_audit_timestamp ON public.audit_logs USING btree ("timestamp");


--
-- TOC entry 3804 (class 1259 OID 16940)
-- Name: idx_audit_user; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_audit_user ON public.audit_logs USING btree (user_id);


--
-- TOC entry 3813 (class 1259 OID 16942)
-- Name: idx_cache_expires; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_cache_expires ON public.cache_entries USING btree (expires_at);


--
-- TOC entry 3807 (class 1259 OID 16938)
-- Name: idx_feedback_query_hash; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_feedback_query_hash ON public.feedback_log USING btree (query_embedding_hash);


--
-- TOC entry 3808 (class 1259 OID 16936)
-- Name: idx_feedback_service; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_feedback_service ON public.feedback_log USING btree (selected_service_id);


--
-- TOC entry 3809 (class 1259 OID 16935)
-- Name: idx_feedback_timestamp; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_feedback_timestamp ON public.feedback_log USING btree ("timestamp");


--
-- TOC entry 3810 (class 1259 OID 16937)
-- Name: idx_feedback_user; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_feedback_user ON public.feedback_log USING btree (user_id);


--
-- TOC entry 3780 (class 1259 OID 16931)
-- Name: idx_interaction_capability_service; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_interaction_capability_service ON public.interaction_capability USING btree (service_id);


--
-- TOC entry 3781 (class 1259 OID 16932)
-- Name: idx_interaction_capability_type; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_interaction_capability_type ON public.interaction_capability USING btree (interaction_type);


--
-- TOC entry 3836 (class 1259 OID 16944)
-- Name: idx_selections_query_hash; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_selections_query_hash ON public.user_selections USING btree (query_embedding_hash);


--
-- TOC entry 3837 (class 1259 OID 16943)
-- Name: idx_selections_service; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_selections_service ON public.user_selections USING btree (selected_service_id);


--
-- TOC entry 3838 (class 1259 OID 16945)
-- Name: idx_selections_timestamp; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_selections_timestamp ON public.user_selections USING btree (created_at);


--
-- TOC entry 3776 (class 1259 OID 16930)
-- Name: idx_service_capability_name; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_service_capability_name ON public.service_capability USING btree (capability_name);


--
-- TOC entry 3777 (class 1259 OID 16929)
-- Name: idx_service_capability_service; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_service_capability_service ON public.service_capability USING btree (service_id);


--
-- TOC entry 3784 (class 1259 OID 16934)
-- Name: idx_service_industry_domain; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_service_industry_domain ON public.service_industry USING btree (domain);


--
-- TOC entry 3785 (class 1259 OID 16933)
-- Name: idx_service_industry_service; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_service_industry_service ON public.service_industry USING btree (service_id);


--
-- TOC entry 3814 (class 1259 OID 16946)
-- Name: idx_service_versions_service; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_service_versions_service ON public.service_versions USING btree (service_id);


--
-- TOC entry 3815 (class 1259 OID 16947)
-- Name: idx_service_versions_tag; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_service_versions_tag ON public.service_versions USING btree (version_tag);


--
-- TOC entry 3769 (class 1259 OID 16927)
-- Name: idx_services_name; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_services_name ON public.services USING btree (name);


--
-- TOC entry 3770 (class 1259 OID 16926)
-- Name: idx_services_status; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_services_status ON public.services USING btree (status);


--
-- TOC entry 3771 (class 1259 OID 16928)
-- Name: idx_services_updated; Type: INDEX; Schema: public; Owner: james
--

CREATE INDEX idx_services_updated ON public.services USING btree (updated_at);


--
-- TOC entry 3868 (class 2620 OID 16951)
-- Name: services update_services_updated_at; Type: TRIGGER; Schema: public; Owner: james
--

CREATE TRIGGER update_services_updated_at BEFORE UPDATE ON public.services FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 3869 (class 2620 OID 16952)
-- Name: users update_users_updated_at; Type: TRIGGER; Schema: public; Owner: james
--

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- TOC entry 3856 (class 2606 OID 16764)
-- Name: access_policy access_policy_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.access_policy
    ADD CONSTRAINT access_policy_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id) ON DELETE CASCADE;


--
-- TOC entry 3862 (class 2606 OID 16874)
-- Name: api_keys api_keys_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.api_keys
    ADD CONSTRAINT api_keys_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3857 (class 2606 OID 16789)
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3858 (class 2606 OID 16805)
-- Name: feedback_log feedback_log_selected_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.feedback_log
    ADD CONSTRAINT feedback_log_selected_service_id_fkey FOREIGN KEY (selected_service_id) REFERENCES public.services(id);


--
-- TOC entry 3859 (class 2606 OID 16810)
-- Name: feedback_log feedback_log_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.feedback_log
    ADD CONSTRAINT feedback_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3854 (class 2606 OID 16716)
-- Name: interaction_capability interaction_capability_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.interaction_capability
    ADD CONSTRAINT interaction_capability_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id) ON DELETE CASCADE;


--
-- TOC entry 3863 (class 2606 OID 16892)
-- Name: query_templates query_templates_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.query_templates
    ADD CONSTRAINT query_templates_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3866 (class 2606 OID 17221)
-- Name: service_agent_protocols service_agent_protocols_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.service_agent_protocols
    ADD CONSTRAINT service_agent_protocols_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id) ON DELETE CASCADE;


--
-- TOC entry 3853 (class 2606 OID 16701)
-- Name: service_capability service_capability_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.service_capability
    ADD CONSTRAINT service_capability_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id) ON DELETE CASCADE;


--
-- TOC entry 3861 (class 2606 OID 16856)
-- Name: service_health service_health_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.service_health
    ADD CONSTRAINT service_health_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id);


--
-- TOC entry 3867 (class 2606 OID 17238)
-- Name: service_industries service_industries_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.service_industries
    ADD CONSTRAINT service_industries_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id) ON DELETE CASCADE;


--
-- TOC entry 3855 (class 2606 OID 16732)
-- Name: service_industry service_industry_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.service_industry
    ADD CONSTRAINT service_industry_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id) ON DELETE CASCADE;


--
-- TOC entry 3865 (class 2606 OID 17200)
-- Name: service_integration_details service_integration_details_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: ai_user
--

ALTER TABLE ONLY public.service_integration_details
    ADD CONSTRAINT service_integration_details_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id) ON DELETE CASCADE;


--
-- TOC entry 3860 (class 2606 OID 16838)
-- Name: service_versions service_versions_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.service_versions
    ADD CONSTRAINT service_versions_service_id_fkey FOREIGN KEY (service_id) REFERENCES public.services(id);


--
-- TOC entry 3864 (class 2606 OID 16921)
-- Name: user_selections user_selections_selected_service_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: james
--

ALTER TABLE ONLY public.user_selections
    ADD CONSTRAINT user_selections_selected_service_id_fkey FOREIGN KEY (selected_service_id) REFERENCES public.services(id);


-- Completed on 2025-06-13 14:30:04 CEST

--
-- PostgreSQL database dump complete
--

