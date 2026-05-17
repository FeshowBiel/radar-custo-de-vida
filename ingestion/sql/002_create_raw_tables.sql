CREATE TABLE IF NOT EXISTS raw.bcb_series (
    id              BIGSERIAL PRIMARY KEY,
    coletado_em     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    codigo_serie    INT NOT NULL,
    nome_serie      VARCHAR(120) NOT NULL,
    categoria       VARCHAR(40),
    unidade         VARCHAR(40),
    data_referencia DATE NOT NULL,
    valor           NUMERIC(18, 6),
    UNIQUE (codigo_serie, data_referencia)
);

CREATE INDEX IF NOT EXISTS idx_bcb_series_codigo ON raw.bcb_series (codigo_serie);
CREATE INDEX IF NOT EXISTS idx_bcb_series_data   ON raw.bcb_series (data_referencia);

CREATE TABLE IF NOT EXISTS raw.ibge_ipca_regional (
    id                BIGSERIAL PRIMARY KEY,
    coletado_em       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    codigo_localidade VARCHAR(20) NOT NULL,
    nome_localidade   VARCHAR(120) NOT NULL,
    data_referencia   DATE NOT NULL,
    variavel          VARCHAR(120),
    valor             NUMERIC(18, 6),
    raw_payload       JSONB,
    UNIQUE (codigo_localidade, data_referencia, variavel)
);

CREATE INDEX IF NOT EXISTS idx_ibge_ipca_local ON raw.ibge_ipca_regional (codigo_localidade);
