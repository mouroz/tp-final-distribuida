# Idiomas

[Inglês](README.md)
[Português](README_PT.md)

# Como executar

Primeiro, certifique-se de que você possui as dependências corretas instaladas. Dentro da pasta raiz do projeto:

```
pip install -r requirements # Se tiver usando pip
```

```
conda env create -f enviroment.yml # Se tiver usando conda
```

```
mamba env create -f enviroment.yml # Se tiver usando mamba
```


# Módulos

## Módulo de Comunicação

Gerencia a estrutura principal (backbone) da comunicação entre o cliente e o servidor, bem como a fila e os mecanismos de replicação ativa. Localizado em src/comm [Veja mais](src/comm/README_PT.md)


## Módulo de Interface
Lógica de interface para a janela da aplicação utilizando PyQt6. Atualmente localizado diretamente em src/ como um arquivo único (src/ui.py).

## Módulos de Teste
Scripts de teste utilizados em toda a aplicação para verificar as funcionalidades.
