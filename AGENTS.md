# AGENTS.md

## Projeto

**Home Integrator** é uma aplicação modular de integração e automação residencial. Atua como camada intermediária entre dispositivos IoT e serviços externos, mantendo as responsabilidades específicas dos sistemas originais.

O projeto deve permanecer **simples, leve, modular, testável e resiliente**, com foco em execução contínua em Raspberry Pi 3 Model B com 1 GB de RAM.

## Stack e restrições

- Python 3.12
- `asyncio` para operações de I/O
- `httpx` para HTTP
- `pydantic-settings` para configuração
- SQLite para persistência local
- Docker e Docker Compose
- Raspberry Pi 3 / 1 GB RAM

Priorize baixo consumo de CPU, memória, armazenamento e rede. Evite dependências, serviços, containers e processamento pesado sem necessidade.

Não introduza PostgreSQL, Redis, microserviços, OpenCV, FFmpeg ou processamento contínuo de vídeo sem uma necessidade real.

## Arquitetura

A organização principal é:

```text
app/
├── main.py
├── config.py
├── domain/
├── infrastructure/
├── integrations/
└── services/

tests/
docs/
data/
```

Responsabilidades:

- `domain/`: modelos e conceitos de negócio. Não deve conhecer APIs externas, HTTP, banco ou infraestrutura.
- `integrations/`: comunicação com sistemas externos, incluindo autenticação, parsing e erros específicos.
- `services/`: regras de negócio, automações e orquestração entre integrações.
- `infrastructure/`: persistência e recursos de infraestrutura.
- `main.py`: inicialização e composição da aplicação; deve permanecer simples.

Fluxo padrão:

```text
Sistema externo
      ↓
Integration
      ↓
Domain
      ↓
Service
      ↓
Integration / Infrastructure
```

### Regra central

Integrações são independentes entre si.

Uma integração **não deve chamar diretamente outra integração** nem conter regras de automação.

Exemplo:

```text
Hikvision → HikvisionEvent → EventProcessor → Telegram
                                      └────→ Sonoff
```

A câmera não deve conhecer Telegram ou Sonoff. O service é responsável por decidir quais ações executar.

## Eventos e automações

O modelo de eventos é o principal mecanismo de comunicação interna.

Novas automações devem ser implementadas em `services/`, e não dentro dos clients ou parsers das integrações.

Quando necessário, automações devem considerar:

- idempotência;
- deduplicação;
- cooldown;
- estado atual do dispositivo;
- timeout;
- retry/backoff;
- fallback.

Ações físicas críticas, como portas, portões, fechaduras e alarmes, não devem ser executadas apenas pela recepção de um evento HTTP sem validação do estado e das condições necessárias.

## Hikvision

A integração Hikvision monitora diretamente as câmeras IP utilizando ISAPI.

Eventos:

```text
/ISAPI/Event/notification/alertStream
```

Snapshot:

```text
/ISAPI/Streaming/channels/101/picture
```

Utilize `httpx` com `httpx.DigestAuth`. Não implemente Digest Authentication manualmente.

O `401 Unauthorized` inicial faz parte do desafio Digest e não deve ser tratado isoladamente como falha de autenticação.

Cada câmera deve possuir sua própria tarefa assíncrona. A indisponibilidade de uma câmera não pode interromper as demais, e a reconexão deve ocorrer automaticamente.

O parser deve fazer somente:

```text
XML → HikvisionEvent
```

Ele não deve enviar notificações, acionar dispositivos, persistir dados ou executar regras de negócio.

Eventos atualmente relevantes para notificações:

```text
eventState == active
AND
targetType IN {human, vehicle}
```

Eventos como `videoloss`, `heartbeat`, `inactive` ou eventos sem `targetType` não devem gerar notificações.

O XML original deve permanecer disponível no evento para diagnóstico/auditoria.

## Snapshot

Snapshots de eventos relevantes devem ser obtidos diretamente da câmera e enviados em memória.

Não salvar imagens em disco, criar arquivos temporários ou armazená-las no SQLite.

O NVR continua responsável pelo armazenamento de vídeo.

## Telegram

A integração Telegram deve somente encapsular a comunicação com a API, incluindo:

- envio de mensagens;
- envio de fotos;
- tratamento de erros HTTP.

A decisão de quando, por que e para quem enviar uma mensagem pertence aos services.

## Persistência

Utilize SQLite para dados locais e pequenos.

Banco padrão:

```text
/data/home_integrator.db
```

Persistência no host:

```text
./data:/data
```

Armazene apenas informações necessárias para integração e histórico.

Alterações estruturais no banco devem utilizar uma estratégia de migração quando necessário. Não dependa de `CREATE TABLE IF NOT EXISTS` para alterar tabelas existentes.

## Configuração e segurança

Configurações específicas do ambiente devem ficar fora do código, preferencialmente em variáveis de ambiente.

Exemplos:

```text
HIKVISION_USERNAME
HIKVISION_PASSWORD
HIKVISION_CAMERAS
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
ALLOWED_TARGET_TYPES
DATABASE_PATH
LOG_LEVEL
```

Nunca versionar `.env` ou credenciais, tokens, API keys e secrets.

`.env.example` deve conter apenas valores fictícios.

Não criar forks do projeto para diferentes instalações. O mesmo código deve atender diferentes ambientes por configuração.

## Concorrência e resiliência

Use `asyncio` para operações de I/O.

Evite criar threads ou processos sem necessidade.

Falhas de uma integração externa não devem derrubar a aplicação inteira.

O comportamento esperado é:

```text
erro → log → retry/reconexão
```

Retries devem possuir intervalo e, quando apropriado, limite e backoff.

Nunca implemente loops de reconexão ocupados sem `await asyncio.sleep(...)`.

## Recursos e armazenamento

A Raspberry Pi 3 é uma restrição arquitetural importante.

Priorize APIs HTTP e recursos fornecidos pelos próprios dispositivos em vez de reproduzir processamento local.

Evite:

- processamento contínuo de vídeo;
- armazenamento contínuo de imagens/vídeos;
- processamento pesado de IA;
- dependências grandes para tarefas simples;
- escrita desnecessária no armazenamento.

Antes de adicionar uma dependência, verifique se Python padrão ou uma dependência já existente resolve o problema.

## Docker

A imagem de produção deve permanecer pequena e adequada à Raspberry Pi 3.

Dependências de desenvolvimento devem permanecer separadas das dependências de runtime.

Durante desenvolvimento, o código pode ser montado:

```yaml
volumes:
  - ./app:/app/app
  - ./data:/data
```

Enquanto `network_mode: host` continuar sendo a forma mais simples de acessar os dispositivos da rede local, mantê-lo.

Alterações somente em Python não devem exigir rebuild:

```bash
docker compose restart home-integrator
```

Rebuild quando houver alterações que afetem a imagem, principalmente:

```bash
docker compose up -d --build
```

após mudanças em `Dockerfile` ou `requirements.txt`.

## Logs

Utilize o módulo `logging`. Não use `print()` para logging operacional.

`INFO` deve ser suficiente para operação normal; `DEBUG` deve ser utilizado para diagnóstico.

O Docker Compose deve limitar o crescimento dos logs com rotação.

## Testes

Testes unitários devem ficar em `tests/` e não depender de hardware real.

Priorize testes para:

- parsers;
- filtros;
- regras de negócio;
- configuração;
- tratamento de eventos.

Testes contra câmeras, NVR, Telegram, Sonoff ou outros equipamentos reais são testes de integração e não devem fazer parte do pipeline padrão sem configuração explícita.

Fixtures reais devem ser sanitizadas antes de serem versionadas.

## Evolução do projeto

Adicione novas integrações em:

```text
app/integrations/<nome>/
```

Adicione novas regras e automações em:

```text
app/services/
```

Comece com a estrutura mínima necessária. Divida módulos ou services somente quando houver responsabilidades claramente diferentes ou crescimento real.

Novas câmeras e dispositivos devem ser adicionados por configuração sempre que possível, sem alteração de código.

Não reorganize o projeto inteiro para uma alteração pequena.

Para mudanças estruturais maiores:

1. identifique o problema;
2. avalie a solução mais simples;
3. preserve compatibilidade;
4. considere impacto em recursos e dados;
5. evite misturar refatoração desnecessária com novas funcionalidades.

## Regras para agentes de IA

Antes de modificar o projeto:

1. Leia este `AGENTS.md`.
2. Respeite a estrutura existente.
3. Faça a menor alteração necessária.
4. Preserve interfaces e funcionalidades existentes.
5. Não introduza arquitetura complexa sem necessidade.
6. Não adicione dependências sem justificativa.
7. Não insira ou altere secrets.
8. Mantenha integrações independentes.
9. Mantenha regras de negócio nos services.
10. Mantenha modelos no domain.
11. Mantenha persistência na infrastructure.
12. Mantenha `main.py` simples.
13. Adicione testes para lógica relevante.
14. Preserve compatibilidade com Python 3.12, Docker, SQLite e Raspberry Pi 3.

### Checklist mental

Antes de implementar uma funcionalidade, determine:

```text
1. Qual sistema externo está envolvido?
2. Qual integração deve encapsular sua comunicação?
3. Qual modelo de domínio representa os dados?
4. Qual service contém a regra de negócio?
5. Há necessidade de persistência?
6. Há configuração específica do ambiente?
7. É necessário teste?
8. Qual é o impacto em recursos?
```

A regra mais importante é:

> O Home Integrator deve crescer em funcionalidades sem crescer desnecessariamente em complexidade.
