# Carona Parque

Um bot no Telegram para ajudar a organizar caronas partindo do Parque Tecnológico da UFRJ.

## Premissas

Para simplificar a versão mínima da aplicação, algumas decisões de projetos foram tomadas:

- O usuário interessado em carona deve se cadastrar pelo bot e aguardar aprovação de administradores
- Todos os destinos possíveis foram divididos em zonas, essas contendo diversas vizinhanças, selecionadas arbitrariamente
- O motorista que desejar fornecer uma carona deverá escolher uma zona e, depois, uma vizinhança como destino, não sendo possível especificar o caminho pelo qual passará pra chegar até lá
- Usuários procurando carona poderão procurar por caronas filtrando por zona e data de partida
- Todas as caronas terão como ponto de partida o ponto de ônibus mais próximo da portaria do Parque Tecnológico da UFRJ

## Desenvolvimento

- Criar um arquivo `.env` semelhante a:

```
POSTGRES_USER="postgres"
POSTGRES_PASSWORD="postgres"
TELEGRAM_TOKEN="<token>"
```

- Executar com:

```
docker-compose build
docker-compose up
```

## Lista de coisas a fazer

- [ ] `/adicionar_carro` (adicionar um carro)
- [ ] `/carros` (listar carros)
- [ ] `/adicionar_carona` (adicionar uma carona)
- [ ] `/caronas` (listar caronas, suas ou todas)
- [ ] Adicionar opção de `/caronas` filtrando por zona e/ou data de partida
- [ ] `/pegar_carona` (alocar uma vaga para uma carona)
- [ ] `/historico` (listar caronas que o usuário já fez)
- [ ] Implementar lembrete 15min antes de partida
