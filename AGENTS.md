# AGENTS.md

# Home Integrator

## 1. Visão geral

O **Home Integrator** é uma aplicação de integração e automação residencial.

O objetivo do projeto é centralizar a comunicação entre dispositivos IoT, câmeras, serviços externos e automações da residência em uma única aplicação leve, modular e de fácil manutenção.

O projeto foi inicialmente desenvolvido para executar em:

- Raspberry Pi 3 Model B
- 1 GB de RAM
- Docker
- Docker Compose

A arquitetura deve continuar priorizando baixo consumo de:

- CPU;
- memória;
- armazenamento;
- rede;
- recursos externos.

O projeto deve evitar complexidade desnecessária.

---

# 2. Objetivo arquitetural

O Home Integrator deve funcionar como uma camada intermediária entre dispositivos e serviços.

```text
┌─────────────────────────────────────────────────────────┐
│                    HOME INTEGRATOR                      │
│                                                         │
│  ┌─────────────┐     ┌─────────────┐                  │
│  │   Domain    │     │  Services   │                  │
│  │             │────>│             │                  │
│  │   Eventos   │     │ Automação   │                  │
│  └─────────────┘     └──────┬──────┘                  │
│                             │                          │
│             ┌───────────────┼───────────────┐          │
│             │               │               │          │
│             ▼               ▼               ▼          │
│       ┌──────────┐    ┌──────────┐    ┌──────────┐   │
│       │Hikvision │    │ Telegram │    │  Sonoff  │   │
│       └──────────┘    └──────────┘    └──────────┘   │
│                                                         │
│                    Infrastructure                      │
│                       SQLite                           │
└─────────────────────────────────────────────────────────┘
```

O Home Integrator não deve substituir os sistemas originais dos fabricantes.

Por exemplo:

- o NVR continua responsável pela gravação;
- as câmeras continuam responsáveis pela detecção;
- o Sonoff continua responsável pelo acionamento;
- o Telegram continua responsável pela entrega das mensagens.

O Home Integrator deve coordenar esses componentes.

---

# 3. Princípios fundamentais

Toda alteração no projeto deve priorizar:

1. Simplicidade.
2. Baixo consumo de recursos.
3. Separação de responsabilidades.
4. Código fácil de entender.
5. Código fácil de testar.
6. Recuperação automática de falhas.
7. Configuração por ambiente.
8. Integrações independentes.
9. Regras de negócio centralizadas.
10. Facilidade para adicionar novas integrações.
11. Facilidade para adicionar novas automações.
12. Compatibilidade com Raspberry Pi 3.
13. Evitar dependências desnecessárias.
14. Evitar serviços externos quando uma solução local simples for suficiente.

---

# 4. Stack principal

## Linguagem

```text
Python 3.12
```

## Runtime

```text
asyncio
```

## HTTP

```text
httpx
```

## Configuração

```text
pydantic-settings
```

## Persistência

```text
SQLite
```

## Containerização

```text
Docker
Docker Compose
```

## Sistema de execução

```text
Raspberry Pi 3 Model B
1 GB RAM
```

---

# 5. Arquitetura de diretórios

A estrutura principal deve seguir:

```text
home-integrator/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   └── events.py
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   └── database.py
│   │
│   ├── integrations/
│   │   ├── __init__.py
│   │   │
│   │   ├── hikvision/
│   │   │   ├── __init__.py
│   │   │   ├── client.py
│   │   │   └── parser.py
│   │   │
│   │   └── telegram/
│   │       ├── __init__.py
│   │       └── client.py
│   │
│   └── services/
│       ├── __init__.py
│       └── event_processor.py
│
├── tests/
│   ├── __init__.py
│   └── test_hikvision_parser.py
│
├── docs/
│   └── architecture.md
│
├── data/
│   └── .gitkeep
│
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── README.md
└── AGENTS.md
```

Essa estrutura deve ser considerada o padrão do projeto.

---

# 6. Responsabilidade de cada camada

## 6.1 `app/domain`

Contém os conceitos fundamentais do Home Integrator.

Exemplo:

```text
app/domain/events.py
```

Deve conter modelos como:

```text
HikvisionEvent
```

O domínio não deve conhecer:

- HTTP;
- Docker;
- Telegram;
- SQLite;
- Hikvision;
- Sonoff;
- eWeLink;
- arquivos;
- APIs externas.

O domínio representa informações e conceitos.

---

# 7. `app/integrations`

Contém todas as integrações externas.

Exemplo atual:

```text
app/integrations/
├── hikvision/
└── telegram/
```

Cada integração deve possuir seu próprio diretório.

Futuras integrações devem seguir:

```text
app/integrations/
├── hikvision/
├── telegram/
├── sonoff/
├── ewelink/
├── mqtt/
├── home_assistant/
└── outras/
```

Não colocar código de uma integração dentro de outra.

---

# 8. Integrações devem ser independentes

Uma integração deve conhecer somente o sistema externo com o qual trabalha.

Exemplo correto:

```text
HikvisionClient
    │
    └── conhece Hikvision
```

```text
TelegramClient
    │
    └── conhece Telegram
```

```text
SonoffClient
    │
    └── conhece Sonoff
```

Evitar:

```text
HikvisionClient
    │
    ├── Telegram
    └── Sonoff
```

A integração Hikvision deve apenas fornecer os eventos.

A decisão sobre o que fazer com o evento pertence à camada de serviço.

---

# 9. Integração Hikvision

A integração Hikvision atualmente é responsável por comunicação direta com as câmeras IP.

O Home Integrator deve monitorar diretamente as câmeras.


---

# 10. Hikvision ISAPI

O monitoramento de eventos utiliza:

```text
/ISAPI/Event/notification/alertStream
```

A captura de imagem utiliza:

```text
/ISAPI/Streaming/channels/101/picture
```

A comunicação deve utilizar:

```python
httpx
```

com:

```python
httpx.DigestAuth
```

Não implementar manualmente o protocolo Digest Authentication.

---

# 11. Autenticação Hikvision

Durante a conexão é esperado:

```text
HTTP 401 Unauthorized
```

seguido de:

```text
HTTP 200 OK
```

O primeiro `401` faz parte do desafio Digest.

Não considerar o primeiro `401` como erro de autenticação.

A conexão somente deve ser considerada falha quando não for possível estabelecer o stream autenticado.

---

# 12. Monitoramento das câmeras

Cada câmera deve possuir uma tarefa independente.

```text
Camera 172.16.0.51
        │
        ▼
     Task #1

Camera 172.16.0.52
        │
        ▼
     Task #2

Camera 172.16.0.53
        │
        ▼
     Task #3
```

Se uma câmera perder conexão:

```text
172.16.0.51 → offline
```

as outras devem continuar:

```text
172.16.0.52 → online
172.16.0.53 → online
```

A câmera indisponível deve realizar reconexão automática.

---

# 13. Modelo de evento

Os eventos Hikvision devem ser convertidos para:

```text
HikvisionEvent
```

Campos:

```text
received_at
camera_ip
event_type
event_state
event_description
channel_id
channel_name
target_type
target_id
raw_xml
```

O XML original deve ser mantido no evento para permitir diagnóstico e auditoria.

---

# 14. Parser Hikvision

O parser deve ser responsável somente por:

```text
XML
 ↓
HikvisionEvent
```

Não deve:

- enviar Telegram;
- acionar Sonoff;
- escrever no banco;
- executar automações;
- decidir se o evento é relevante.

A regra de negócio deve ser executada posteriormente.

---

# 15. Eventos relevantes

Atualmente, somente os eventos classificados como:

```text
targetType = human
```

ou:

```text
targetType = vehicle
```

são relevantes para notificações.

Além disso:

```text
eventState = active
```

é obrigatório.

Regra:

```text
eventState == active
AND
targetType IN {human, vehicle}
```

---

# 16. Eventos irrelevantes

Eventos como:

```text
videoloss
heartbeat
inactive
eventos sem targetType
```

não devem gerar notificações.

Eles podem continuar sendo persistidos para diagnóstico.

---

# 17. Processamento de eventos

O processamento deve ocorrer em:

```text
app/services/
```

Atualmente:

```text
app/services/event_processor.py
```

Esse componente é responsável por transformar um evento em uma ação de negócio.

```text
HikvisionEvent
      │
      ▼
EventProcessor
      │
      ├── verificar relevância
      ├── salvar evento
      ├── solicitar snapshot
      └── enviar Telegram
```

---

# 18. Regra importante

As integrações não devem possuir regras de automação.

Errado:

```text
HikvisionClient
    └── se pessoa:
            chamar Telegram
```

Errado:

```text
HikvisionClient
    └── se veículo:
            ligar Sonoff
```

Correto:

```text
HikvisionClient
        │
        ▼
HikvisionEvent
        │
        ▼
EventProcessor
        │
        ├── Telegram
        │
        └── Sonoff
```

---

# 19. Telegram

A integração Telegram deve ficar em:

```text
app/integrations/telegram/
```

Responsabilidades:

- enviar mensagens;
- enviar fotos;
- tratar comunicação HTTP com a API do Telegram.

Não deve decidir:

- quando enviar;
- qual evento enviar;
- quando ligar uma luz;
- quando ignorar um evento.

Essas decisões pertencem aos services.

---

# 20. Snapshot

Quando um evento relevante ocorrer, o Home Integrator deve solicitar uma imagem diretamente da câmera.

Fluxo:

```text
Evento
   │
   ▼
targetType human/vehicle
   │
   ▼
GET snapshot
   │
   ▼
bytes
   │
   ▼
Telegram
```

O snapshot deve permanecer somente na memória.

Não salvar:

```text
.jpg
.jpeg
.png
```

no disco.

Não criar arquivos temporários.

Não armazenar imagens no SQLite.

Isso reduz:

- escrita no cartão SD;
- utilização de armazenamento;
- complexidade;
- necessidade de limpeza.

---

# 21. SQLite

O banco atual é SQLite.

Dentro do container:

```text
/data/home_integrator.db
```

No host:

```text
./data/home_integrator.db
```

O diretório deve ser persistente:

```yaml
volumes:
  - ./data:/data
```

O SQLite deve ser utilizado para informações pequenas e locais.

Não introduzir PostgreSQL, MySQL ou outro banco sem uma necessidade real.

---

# 22. Banco de dados

O banco atualmente registra eventos.

Campos principais:

```text
id
received_at
camera_ip
event_type
event_state
event_description
channel_id
channel_name
target_type
target_id
payload
```

O campo:

```text
payload
```

deve armazenar o XML original do evento.

---

# 23. Migrações de banco

Ao modificar a estrutura do SQLite:

```text
NÃO
```

simplesmente assumir que:

```sql
CREATE TABLE IF NOT EXISTS
```

irá atualizar a tabela.

Para alterações estruturais futuras, utilizar uma estratégia de migração.

Enquanto o projeto for pequeno, uma implementação simples pode ser utilizada.

Exemplo futuro:

```text
app/infrastructure/
├── database.py
└── migrations/
    ├── 001_initial.sql
    ├── 002_add_camera.sql
    └── 003_add_automation.sql
```

Quando a quantidade de alterações justificar, pode ser introduzido um sistema de migrations.

Não adicionar uma ferramenta de migrations apenas por antecipação.

---

# 24. Configuração

Configurações externas devem ficar em variáveis de ambiente.

Exemplo:

```env
HIKVISION_USERNAME=admin
HIKVISION_PASSWORD=CHANGE_ME

HIKVISION_CAMERAS=172.16.0.51,172.16.0.52,172.16.0.53

TELEGRAM_BOT_TOKEN=CHANGE_ME
TELEGRAM_CHAT_ID=CHANGE_ME

ALLOWED_TARGET_TYPES=human,vehicle

DATABASE_PATH=/data/home_integrator.db

LOG_LEVEL=INFO
```

---

# 25. Segurança

Nunca versionar:

```text
.env
```

Nunca colocar credenciais em:

```text
.py
.yaml
.yml
.md
.json
.xml
```

Nunca colocar em commits:

- senha Hikvision;
- token Telegram;
- token eWeLink;
- senha Sonoff;
- API keys;
- secrets.

O arquivo:

```text
.env.example
```

deve conter somente valores fictícios.

---

# 26. Timezone

O timezone de apresentação deve ser:

```text
America/Sao_Paulo
```

Não depender do timezone do container.

Não depender do timezone da Raspberry Pi.

Conversões de horário devem ser explícitas.

Exemplo:

```python
ZoneInfo("America/Sao_Paulo")
```

---

# 27. Logs

A aplicação deve utilizar:

```python
logging
```

Não utilizar `print()` para logging operacional.

Níveis:

```text
DEBUG
INFO
WARNING
ERROR
EXCEPTION
```

`INFO` deve ser suficiente para operação normal.

`DEBUG` pode ser utilizado durante diagnóstico.

---

# 28. Logs Docker

O Docker Compose deve possuir rotação:

```yaml
logging:
  driver: json-file
  options:
    max-size: "10m"
    max-file: "3"
```

Isso limita o crescimento dos logs.

Não implementar rotação manual dentro da aplicação.

---

# 29. Docker

O Dockerfile deve permanecer pequeno.

Evitar instalar:

- compiladores;
- ferramentas de desenvolvimento;
- pacotes desnecessários;
- bibliotecas multimídia pesadas.

A imagem deve ser adequada à Raspberry Pi 3.

---

# 30. Docker Compose

O código deve continuar montado durante desenvolvimento:

```yaml
volumes:
  - ./app:/app/app
```

O banco deve continuar persistente:

```yaml
volumes:
  - ./data:/data
```

A aplicação deve utilizar:

```yaml
network_mode: host
```

enquanto essa estratégia continuar sendo a maneira mais simples de acessar os dispositivos da rede local.

---

# 31. Desenvolvimento

Alterações somente em Python não devem exigir rebuild.

Após modificar:

```text
app/
```

executar:

```bash
docker compose restart home-integrator
```

Rebuild somente quando necessário:

```bash
docker compose up -d --build
```

Principalmente após alterações em:

```text
Dockerfile
requirements.txt
```

---

# 32. Testes

Os testes devem ficar em:

```text
tests/
```

Testes unitários devem evitar depender de hardware real.

Priorizar testes para:

- parser;
- filtros;
- regras de negócio;
- formatação;
- configuração;
- tratamento de eventos.

Exemplo:

```text
tests/
├── test_hikvision_parser.py
├── test_event_processor.py
└── test_configuration.py
```

---

# 33. Testes com dispositivos reais

Testes que dependem de:

- câmera;
- NVR;
- Sonoff;
- Telegram;
- eWeLink;

não devem ser testes unitários.

Devem ser considerados testes de integração.

Nunca fazer testes automatizados agressivos contra dispositivos físicos.

---

# 34. Fixtures

XMLs reais utilizados para testes podem ser armazenados como fixtures.

Exemplo:

```text
tests/
└── fixtures/
    └── hikvision/
        ├── human.xml
        ├── vehicle.xml
        └── videoloss.xml
```

Antes de salvar qualquer fixture:

- remover credenciais;
- remover tokens;
- remover informações sensíveis;
- remover dados desnecessários.

---

# 35. Novas integrações

Quando uma nova tecnologia ou dispositivo for adicionado, seguir o padrão:

```text
app/integrations/<nome>/
```

Exemplo:

```text
app/integrations/sonoff/
├── __init__.py
└── client.py
```

Se a integração possuir várias responsabilidades:

```text
app/integrations/sonoff/
├── __init__.py
├── client.py
├── parser.py
├── models.py
└── exceptions.py
```

Não criar arquivos antecipadamente sem necessidade.

Começar simples.

---

# 36. Novas integrações IoT

Exemplo futuro:

```text
app/integrations/
├── hikvision/
├── telegram/
├── sonoff/
└── ewelink/
```

A implementação deve encapsular:

```text
Integration
    │
    ├── comunicação externa
    ├── autenticação
    ├── parsing
    └── erros específicos
```

A integração não deve controlar o fluxo geral da aplicação.

---

# 37. Novos dispositivos

Se forem adicionados outros dispositivos:

```text
sensor
lâmpada
interruptor
tomada
fechadura
alarme
TV
ar-condicionado
```

não criar código diretamente no `main.py`.

Exemplo:

```text
app/integrations/
├── hikvision/
├── telegram/
├── sonoff/
├── samsung/
├── tuya/
└── mqtt/
```

---

# 38. Novas automações

Automações pertencem a:

```text
app/services/
```

Exemplo:

```text
app/services/
├── event_processor.py
├── notification_service.py
├── lighting_service.py
└── security_service.py
```

Não colocar todas as automações em um único arquivo gigante.

---

# 39. Evolução dos services

Inicialmente:

```text
app/services/
└── event_processor.py
```

Se crescer:

```text
app/services/
├── event_processor.py
├── notification_service.py
├── lighting_service.py
├── security_service.py
└── automation_service.py
```

A divisão deve ocorrer somente quando houver responsabilidade real a separar.

---

# 40. Exemplo de automação futura

```text
Pessoa detectada
        │
        ▼
Hikvision
        │
        ▼
HikvisionEvent
        │
        ▼
EventProcessor
        │
        ├───────────────┐
        ▼               ▼
    Telegram          Sonoff
        │               │
        ▼               ▼
      Foto          Liga luz
```

A câmera não sabe que existe Sonoff.

O Sonoff não sabe que existe Hikvision.

O service conhece ambos.

---

# 41. Eventos como base de automação

O modelo de eventos deve ser considerado o principal mecanismo de comunicação interna.

```text
Hikvision
   │
   ▼
Event
   │
   ├── Telegram
   ├── Sonoff
   ├── Log
   └── outras automações
```

Isso permite que uma mesma ocorrência gere múltiplas ações.

---

# 42. Evitar acoplamento

Evitar:

```python
from app.integrations.sonoff.client import SonoffClient
```

dentro de:

```text
app/integrations/hikvision/
```

Evitar:

```python
from app.integrations.hikvision.client import HikvisionClient
```

dentro de:

```text
app/integrations/telegram/
```

As integrações devem permanecer independentes.

---

# 43. Fluxo recomendado

O fluxo padrão deve ser:

```text
EXTERNAL DEVICE
      │
      ▼
INTEGRATION
      │
      ▼
DOMAIN MODEL
      │
      ▼
SERVICE
      │
      ├── persistence
      ├── integration A
      ├── integration B
      └── integration C
```

Esse padrão deve ser mantido para novas funcionalidades.

---

# 44. Novas implantações

Quando o Home Integrator passar a controlar novos ambientes ou instalações, não duplicar o código da aplicação.

A aplicação deve ser configurada através do ambiente.

Exemplo:

```text
Instalação A
    │
    ├── .env
    ├── data/
    └── docker-compose.yml

Instalação B
    │
    ├── .env
    ├── data/
    └── docker-compose.yml
```

O código deve continuar o mesmo.

Somente as configurações devem variar quando possível.

---

# 45. Configuração por ambiente

Valores específicos da instalação devem ficar fora do código.

Exemplos:

```text
IPs
credenciais
tokens
chat IDs
nomes
timeouts
features
```

Devem ser configuráveis através de:

```text
.env
```

ou futuramente:

```text
config/
```

caso a quantidade de configuração cresça significativamente.

---

# 46. Não criar forks para instalações

Evitar criar:

```text
home-integrator-casa
home-integrator-escritorio
home-integrator-outro
```

O projeto deve permanecer único.

Diferenças entre instalações devem ser tratadas por configuração.

---

# 47. Feature flags

Se uma funcionalidade precisar ser habilitada/desabilitada por instalação, utilizar configuração.

Exemplo futuro:

```env
ENABLE_TELEGRAM=true
ENABLE_SONOFF=true
ENABLE_CAMERA_SNAPSHOTS=true
```

Não criar código específico para uma residência.

---

# 48. Novas câmeras

Adicionar novas câmeras não deve exigir alteração de código.

A configuração deve permitir:

```env
HIKVISION_CAMERAS=172.16.0.51,172.16.0.52,172.16.0.53
```

Novos IPs podem ser adicionados:

```env
HIKVISION_CAMERAS=172.16.0.51,172.16.0.52,172.16.0.53,172.16.0.54
```

O código deve criar uma tarefa para cada câmera.

---

# 49. Nomes de dispositivos

Quando possível, utilizar informações fornecidas pelo próprio dispositivo:

```text
channelName
deviceName
deviceDescription
```

Não codificar nomes de câmeras diretamente no código.

---

# 50. Erros

Integrações externas podem falhar.

Exemplos:

```text
camera offline
Telegram indisponível
Sonoff offline
timeout
HTTP 401
HTTP 500
network failure
```

A aplicação não deve encerrar completamente por causa de uma falha de integração.

Quando possível:

```text
erro
  │
  ▼
log
  │
  ▼
retry
```

---

# 51. Retry

Retries devem possuir:

- intervalo;
- limite quando apropriado;
- backoff quando necessário.

Evitar loops de retry sem intervalo.

Nunca executar:

```python
while True:
    connect()
```

sem:

```python
await asyncio.sleep(...)
```

em caso de falha.

---

# 52. Concorrência

Utilizar `asyncio` para operações de I/O.

Exemplos:

- câmeras;
- Telegram;
- APIs;
- Sonoff;
- eWeLink;
- MQTT.

Não criar threads para cada câmera sem necessidade.

Não criar processos adicionais sem necessidade.

---

# 53. Raspberry Pi

A Raspberry Pi 3 possui apenas 1 GB de RAM.

Portanto, evitar:

```text
OpenCV
FFmpeg
processamento contínuo de vídeo
modelos de IA locais pesados
bancos externos
containers desnecessários
```

quando a funcionalidade puder ser realizada através de APIs HTTP simples.

---

# 54. Processamento de vídeo

O Home Integrator não deve processar streams de vídeo continuamente se o dispositivo já fornece eventos inteligentes.

Preferir:

```text
Camera
  │
  ├── detecta pessoa
  ├── detecta veículo
  │
  ▼
alertStream
  │
  ▼
Home Integrator
```

em vez de:

```text
Camera
  │
  ▼
RTSP
  │
  ▼
Raspberry Pi
  │
  ▼
processamento de vídeo
```

A detecção deve permanecer na câmera quando possível.

---

# 55. Armazenamento

O armazenamento da Raspberry Pi deve ser preservado.

Não armazenar continuamente:

- imagens;
- vídeos;
- snapshots;
- logs gigantes;
- dados temporários.

O NVR é responsável pelo armazenamento de vídeo.

O Home Integrator deve armazenar apenas informações necessárias para integração e histórico.

---

# 56. Dependências

Antes de adicionar uma biblioteca:

1. Verificar se a funcionalidade pode ser implementada com Python padrão.
2. Verificar se uma dependência existente já resolve o problema.
3. Avaliar impacto na Raspberry Pi.
4. Avaliar tamanho da imagem Docker.
5. Avaliar manutenção da biblioteca.
6. Adicionar somente se realmente necessário.

Evitar dependências para funcionalidades triviais.

---

# 57. requirements.txt

Deve conter somente dependências necessárias para execução.

Dependências de desenvolvimento devem ficar separadas.

Exemplo:

```text
requirements.txt
requirements-dev.txt
```

Não instalar ferramentas de desenvolvimento desnecessariamente na imagem de produção.

---

# 58. Testes de integração

Testes reais contra equipamentos devem ser executados conscientemente.

Exemplo:

```text
tests/integration/
```

Futuramente:

```text
tests/
├── unit/
└── integration/
```

Os testes de integração podem exigir:

```text
Hikvision real
Telegram real
Sonoff real
```

e não devem ser executados automaticamente em todos os builds sem configuração apropriada.

---

# 59. CI/CD futuro

Quando CI/CD for adicionado, o pipeline deve executar pelo menos:

```text
lint
    │
    ▼
unit tests
    │
    ▼
build
```

Testes físicos de equipamentos não devem fazer parte do pipeline padrão.

---

# 60. Versionamento

O projeto deve utilizar Git.

Commits devem ser objetivos.

Exemplos:

```text
feat: add sonoff integration
feat: add human detection notification
fix: reconnect hikvision stream
fix: convert notification timezone
refactor: organize integration modules
test: add hikvision vehicle event fixture
docs: update architecture
```

---

# 61. Mudanças arquiteturais

Antes de realizar uma mudança estrutural grande, verificar:

1. Se realmente existe necessidade.
2. Se a solução pode ser implementada de maneira menor.
3. Se a mudança melhora a manutenção.
4. Se a mudança aumenta o consumo da Raspberry.
5. Se afeta instalações existentes.
6. Se exige migração de dados.
7. Se exige alteração de configuração.

Não introduzir arquitetura complexa apenas por antecipação.

---

# 62. Quando dividir um módulo

Um arquivo deve ser dividido quando possuir responsabilidades claramente diferentes.

Exemplo:

```text
client.py
```

pode inicialmente conter:

```text
HTTP
autenticação
snapshot
stream
```

Se crescer demais, dividir:

```text
client.py
stream.py
snapshot.py
auth.py
```

Não dividir prematuramente.

---

# 63. Quando criar um novo service

Criar um novo service quando existir uma responsabilidade de negócio independente.

Exemplo:

```text
event_processor.py
```

pode inicialmente tratar tudo.

Quando crescer:

```text
event_processor.py
notification_service.py
lighting_service.py
security_service.py
```

A divisão deve acompanhar o crescimento real do sistema.

---

# 64. Estrutura futura recomendada

Quando o projeto crescer significativamente, a estrutura poderá evoluir para:

```text
home-integrator/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   │
│   ├── domain/
│   │   ├── events.py
│   │   ├── devices.py
│   │   ├── automations.py
│   │   └── notifications.py
│   │
│   ├── infrastructure/
│   │   ├── database.py
│   │   ├── logging.py
│   │   └── migrations/
│   │
│   ├── integrations/
│   │   ├── hikvision/
│   │   ├── telegram/
│   │   ├── sonoff/
│   │   ├── ewelink/
│   │   └── mqtt/
│   │
│   └── services/
│       ├── event_processor.py
│       ├── notification_service.py
│       ├── lighting_service.py
│       ├── security_service.py
│       └── automation_service.py
│
├── tests/
│   ├── unit/
│   └── integration/
│
├── docs/
│   ├── architecture.md
│   ├── integrations/
│   └── automations/
│
├── data/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── .dockerignore
├── README.md
└── AGENTS.md
```

Essa estrutura não deve ser criada inteira antecipadamente.

Ela representa uma possível evolução.

Criar somente os diretórios necessários conforme funcionalidades forem implementadas.

---

# 65. Organização de documentação

O `README.md` deve permanecer simples e voltado para:

- descrição;
- instalação;
- configuração;
- execução;
- comandos básicos.

O `AGENTS.md` é responsável pelas regras arquiteturais e de desenvolvimento assistido por IA.

Documentação técnica detalhada deve ficar em:

```text
docs/
```

Exemplo:

```text
docs/
├── architecture.md
├── integrations/
│   ├── hikvision.md
│   ├── telegram.md
│   └── sonoff.md
│
└── automations/
    ├── security.md
    └── lighting.md
```

---

# 66. Documentação de novas integrações

Toda integração importante deve possuir documentação própria quando sua complexidade justificar.

Exemplo:

```text
docs/integrations/sonoff.md
```

Deve explicar:

- objetivo;
- autenticação;
- endpoints;
- configuração;
- limitações;
- dependências;
- comportamento em caso de falha;
- exemplos de uso.

---

# 67. Documentação de automações

Automações complexas devem ser documentadas.

Exemplo:

```text
docs/automations/security.md
```

Descrever:

```text
Evento
  ↓
Condições
  ↓
Ações
  ↓
Fallback
```

---

# 68. Regra para novas funcionalidades

Ao implementar uma nova funcionalidade:

1. Identificar o domínio.
2. Identificar se existe integração externa.
3. Implementar a integração isoladamente.
4. Criar ou atualizar o modelo de domínio.
5. Implementar a regra no service.
6. Persistir somente se necessário.
7. Adicionar testes.
8. Atualizar documentação quando necessário.
9. Verificar consumo de recursos.
10. Verificar compatibilidade com Raspberry Pi.

---

# 69. Exemplo: adicionar Sonoff

A implementação futura deve seguir aproximadamente:

```text
1. Criar:

app/integrations/sonoff/

2. Implementar:

SonoffClient

3. Configurar:

SONOFF_...

4. Criar regra em:

app/services/

5. Testar:

SonoffClient

6. Integrar:

EventProcessor
```

Não alterar:

```text
HikvisionClient
```

para chamar diretamente o Sonoff.

---

# 70. Exemplo: adicionar eWeLink

Caso o controle do Sonoff seja realizado através de eWeLink:

```text
app/integrations/ewelink/
```

A integração eWeLink deve encapsular:

- autenticação;
- tokens;
- chamadas HTTP;
- dispositivos;
- estados;
- comandos.

O service decide quando chamar a integração.

---

# 71. Exemplo de arquitetura com Sonoff

```text
                  Hikvision
                     │
                     ▼
               HikvisionEvent
                     │
                     ▼
               EventProcessor
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
      Telegram                Sonoff
          │                     │
          ▼                     ▼
       snapshot              luz ligada
```

Nenhuma integração precisa conhecer a outra.

---

# 72. Resiliência

Uma falha em uma integração não deve derrubar a aplicação inteira.

Exemplo:

```text
Telegram OFFLINE
      │
      ├── Hikvision continua
      ├── SQLite continua
      └── Sonoff continua
```

Exemplo:

```text
Sonoff OFFLINE
      │
      ├── Hikvision continua
      ├── Telegram continua
      └── SQLite continua
```

Os erros devem ser registrados.

---

# 73. Idempotência

Automação deve evitar executar ações repetidamente quando o mesmo evento for recebido várias vezes.

Se necessário, implementar:

```text
event_id
event timestamp
cooldown
deduplication
```

antes de acionar dispositivos físicos.

Isso é especialmente importante para:

```text
luzes
portas
portões
alarmes
```

---

# 74. Cooldown

Automação futura pode utilizar cooldown.

Exemplo:

```text
Pessoa detectada
     │
     ▼
Ligar luz
     │
     ▼
Bloquear novas ativações
por 30 segundos
```

O cooldown deve ser implementado no service.

Não no cliente Hikvision.

---

# 75. Estado de dispositivos

Quando necessário, o Home Integrator pode manter estado dos dispositivos.

Exemplo:

```text
Sonoff:
    ligado
    desligado
    indisponível
```

Esse estado pertence ao domínio ou service apropriado.

Não colocar lógica de estado dentro do parser da integração.

---

# 76. Segurança residencial

Caso o projeto passe a controlar:

- fechaduras;
- portões;
- alarmes;
- portas;

as automações devem possuir atenção especial para:

- estado atual;
- confirmação;
- timeout;
- fallback;
- indisponibilidade;
- idempotência.

Não executar ações críticas simplesmente porque um evento HTTP foi recebido.

---

# 77. Compatibilidade

Ao alterar qualquer componente:

Verificar:

```text
Python 3.12
Raspberry Pi 3
Docker
Docker Compose
SQLite
```

Evitar recursos que dependam de hardware moderno sem necessidade.

---

# 78. Regra de simplicidade

A pergunta principal antes de implementar qualquer funcionalidade deve ser:

> Existe uma maneira mais simples de fazer isso utilizando uma API já fornecida pelo dispositivo?

Exemplo:

Se a câmera já fornece:

```text
targetType=human
```

não instalar um modelo de IA para reconhecer pessoas.

Se a câmera já fornece:

```text
snapshot
```

não utilizar FFmpeg para extrair frames.

Se o Telegram aceita:

```text
multipart/form-data
```

não salvar a imagem no disco antes de enviar.

---

# 79. Regra para agentes de IA

Agentes de IA trabalhando no repositório devem:

1. Ler este `AGENTS.md` antes de modificar o projeto.
2. Respeitar a estrutura existente.
3. Evitar reorganizações desnecessárias.
4. Não criar arquitetura complexa sem necessidade.
5. Não alterar interfaces existentes sem motivo.
6. Não remover funcionalidades existentes sem autorização.
7. Não substituir tecnologias sem justificativa.
8. Preservar compatibilidade com Raspberry Pi 3.
9. Não inserir credenciais.
10. Não alterar `.env` com secrets.
11. Criar testes quando adicionar lógica relevante.
12. Manter integrações independentes.
13. Manter regras de negócio nos services.
14. Manter comunicação externa nas integrations.
15. Manter modelos no domain.
16. Manter persistência na infrastructure.
17. Manter `main.py` simples.

---

# 80. Regra para modificações pequenas

Para uma alteração pequena:

```text
NÃO
```

reorganizar o projeto inteiro.

Exemplo:

Se o objetivo é alterar timezone:

```text
alterar somente o componente responsável
```

Se o objetivo é adicionar snapshot:

```text
alterar somente Hikvision + Telegram + service
```

Não modificar Docker sem necessidade.

---

# 81. Regra para modificações estruturais

Antes de uma grande refatoração:

1. Identificar o problema.
2. Identificar a estrutura atual.
3. Identificar o benefício.
4. Garantir compatibilidade.
5. Dividir a alteração em etapas.
6. Evitar misturar refatoração com funcionalidade sem necessidade.

---

# 82. O que não fazer

```text
❌ colocar lógica de negócio em clients
❌ colocar chamadas Telegram no Hikvision
❌ colocar chamadas Sonoff no Hikvision
❌ colocar SQL nos services
❌ colocar SQL nas integrations
❌ colocar credenciais no código
❌ salvar snapshots no disco
❌ processar vídeo continuamente sem necessidade
❌ criar containers para cada pequena funcionalidade
❌ criar microserviços sem necessidade
❌ adicionar Redis sem necessidade
❌ adicionar PostgreSQL sem necessidade
❌ instalar OpenCV sem necessidade
❌ instalar FFmpeg sem necessidade
❌ criar threads para cada câmera sem necessidade
❌ criar arquivos sem responsabilidade clara
❌ duplicar o projeto para cada residência
```

---

# 83. O que fazer

Priorizar:

```text
✅ APIs oficiais dos dispositivos
✅ asyncio
✅ HTTPX
✅ SQLite
✅ Docker
✅ configuração por ambiente
✅ integrações independentes
✅ services para automações
✅ modelos de domínio
✅ logs estruturados
✅ retry
✅ reconexão
✅ testes unitários
✅ baixo consumo de recursos
```

---

# 84. Estado atual do projeto

Atualmente o Home Integrator possui:

```text
Hikvision
    │
    ├── monitoramento direto das câmeras
    ├── Digest Authentication
    ├── alertStream
    ├── detecção human
    ├── detecção vehicle
    └── snapshot

Telegram
    │
    ├── mensagens
    └── fotos

SQLite
    │
    └── histórico de eventos
```

Câmeras atuais:

```text
172.16.0.51
172.16.0.52
172.16.0.53
```

NVR:

```text
172.16.0.50
```

---

# 85. Roadmap arquitetural

A evolução esperada pode seguir:

```text
FASE 1
Hikvision
   │
   └── Telegram
```

Depois:

```text
FASE 2
Hikvision
   │
   ├── Telegram
   └── Sonoff
```

Depois:

```text
FASE 3
Hikvision
   │
   ├── Telegram
   ├── Sonoff
   └── eWeLink
```

Depois:

```text
FASE 4

                    Home Integrator
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
    Segurança          Iluminação          Notificação
        │                  │                  │
    Hikvision           Sonoff             Telegram
        │                  │
      NVR                eWeLink
```

---

# 86. Arquitetura final desejada

A arquitetura de longo prazo deve permitir:

```text
                    ┌───────────────┐
                    │ Home Integr.  │
                    └───────┬───────┘
                            │
              ┌─────────────┼─────────────┐
              │             │             │
              ▼             ▼             ▼
          Devices        Services     Persistence
              │             │             │
      ┌───────┼───────┐     │          SQLite
      │       │       │     │
      ▼       ▼       ▼     │
   Camera  Sonoff   MQTT    │
      │       │       │     │
      └───────┴───────┘     │
              │             │
              └──────┬──────┘
                     │
                     ▼
                 Automations
                     │
             ┌───────┴───────┐
             ▼               ▼
         Telegram          Actions
```

O Home Integrator deve permanecer como **um único projeto modular**, mesmo quando o número de integrações crescer.

---

# 87. Regra final de arquitetura

Sempre que uma nova funcionalidade for solicitada, primeiro identificar:

```text
1. Qual é o dispositivo ou serviço externo?
2. Qual é o modelo de domínio envolvido?
3. Qual é a integração responsável pela comunicação?
4. Qual é a regra de negócio?
5. Qual service deve executar essa regra?
6. Precisa de persistência?
7. Precisa de configuração?
8. Precisa de testes?
9. Qual o impacto na Raspberry Pi?
```

A implementação deve seguir:

```text
EXTERNAL SYSTEM
       │
       ▼
   INTEGRATION
       │
       ▼
     DOMAIN
       │
       ▼
     SERVICE
       │
       ├── INTEGRATION
       ├── INTEGRATION
       └── INFRASTRUCTURE
```

Essa separação deve ser preservada durante toda a evolução do Home Integrator.

---

# 88. Regra mais importante

O Home Integrator deve crescer em funcionalidades sem crescer desnecessariamente em complexidade.

Adicionar:

```text
novos dispositivos
novas integrações
novas automações
novas notificações
novos sensores
```

não deve exigir reescrever a arquitetura existente.

A estrutura deve permitir crescimento incremental:

```text
Integração
    ↓
Modelo
    ↓
Service
    ↓
Automação
```

Mantendo o sistema:

```text
simples
modular
leve
testável
resiliente
```

e adequado para execução contínua em uma Raspberry Pi 3 Model B com 1 GB de RAM.
