-- Cria a tabela
CREATE TABLE IF NOT EXISTS app_usage_logs (
    id BIGSERIAL PRIMARY KEY,
    
    -- Informações do usuário
    tipo_usuario VARCHAR(50) NOT NULL,
    secretaria VARCHAR(255),
    instituicao_parceira VARCHAR(255),
    
    -- Informações da sessão
    session_id VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    
    -- Informações do processamento
    tipo_funcionalidade VARCHAR(50) NOT NULL,
    nome_modulo VARCHAR(255),
    tipo_modulo VARCHAR(255),
    nome_arquivo VARCHAR(500),
    quantidade_linhas INTEGER,
    
    -- Metadados
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Remove índices antigos se existirem (opcional)
DROP INDEX IF EXISTS idx_app_usage_logs_tipo_usuario;
DROP INDEX IF EXISTS idx_app_usage_logs_session_id;
DROP INDEX IF EXISTS idx_app_usage_logs_created_at;
DROP INDEX IF EXISTS idx_app_usage_logs_tipo_funcionalidade;
DROP INDEX IF EXISTS idx_app_usage_logs_nome_modulo;

-- Cria os índices
CREATE INDEX idx_app_usage_logs_tipo_usuario ON app_usage_logs(tipo_usuario);
CREATE INDEX idx_app_usage_logs_session_id ON app_usage_logs(session_id);
CREATE INDEX idx_app_usage_logs_created_at ON app_usage_logs(created_at);
CREATE INDEX idx_app_usage_logs_tipo_funcionalidade ON app_usage_logs(tipo_funcionalidade);
CREATE INDEX idx_app_usage_logs_nome_modulo ON app_usage_logs(nome_modulo);

-- Verifica se a tabela foi criada corretamente
SELECT 
    column_name, 
    data_type, 
    is_nullable
FROM information_schema.columns
WHERE table_name = 'app_usage_logs'
ORDER BY ordinal_position;
