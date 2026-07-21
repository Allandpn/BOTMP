-- =====================================================
-- ESTADO
-- =====================================================

CREATE TABLE IF NOT EXISTS estado (

    id INTEGER PRIMARY KEY CHECK(id = 1),

    ultima_edicao INTEGER NOT NULL,

    ultimo_ano INTEGER NOT NULL,

    ultima_atualizacao TEXT NOT NULL
);

-- =====================================================
-- EDICOES
-- =====================================================

CREATE TABLE IF NOT EXISTS edicoes (

    id INTEGER PRIMARY KEY,

    numero INTEGER NOT NULL,

    ano INTEGER NOT NULL,

    url TEXT NOT NULL,

    data_download TEXT NOT NULL,

    processada INTEGER NOT NULL DEFAULT 0,

    UNIQUE(numero, ano)
);

CREATE INDEX IF NOT EXISTS idx_edicoes_numero
ON edicoes(numero, ano);

-- =====================================================
-- OCORRENCIAS
-- =====================================================

CREATE TABLE IF NOT EXISTS ocorrencias (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    edicao_id INTEGER NOT NULL,

    pagina INTEGER NOT NULL,

    expressao TEXT NOT NULL,

    tipo_busca TEXT NOT NULL,

    contexto TEXT NOT NULL,

    data_encontrada TEXT NOT NULL,

    FOREIGN KEY(edicao_id)
        REFERENCES edicoes(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ocorrencias_edicao
ON ocorrencias(edicao_id);

-- =====================================================
-- CLASSIFICACOES IA
-- =====================================================

CREATE TABLE IF NOT EXISTS classificacoes_ia (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    ocorrencia_id INTEGER NOT NULL,

    resultado TEXT NOT NULL,

    confianca REAL,

    modelo TEXT,

    justificativa TEXT,

    data_classificacao TEXT NOT NULL,

    FOREIGN KEY(ocorrencia_id)
        REFERENCES ocorrencias(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_classificacoes_ocorrencia
ON classificacoes_ia(ocorrencia_id);

-- =====================================================
-- NOTIFICACOES
-- =====================================================

CREATE TABLE IF NOT EXISTS notificacoes (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    ocorrencia_id INTEGER NOT NULL,

    canal TEXT NOT NULL,

    status TEXT NOT NULL,

    tentativas INTEGER NOT NULL DEFAULT 0,

    data_envio TEXT,

    erro TEXT,

    FOREIGN KEY(ocorrencia_id)
        REFERENCES ocorrencias(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_notificacoes_ocorrencia
ON notificacoes(ocorrencia_id);



CREATE INDEX IF NOT EXISTS idx_notificacoes_status ON notificacoes(status);