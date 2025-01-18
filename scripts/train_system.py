#!/usr/bin/env python3
import click
from pathlib import Path
from src.training import Pronto4GLTrainer

@click.command()
@click.argument('code_directory', type=click.Path(exists=True))
@click.option('--persist-dir', default='data/chroma', help='ChromaDB persistence directory')
def train(code_directory: str, persist_dir: str):
    """Train the Pronto 4GL Assistant with code from the specified directory."""
    try:
        trainer = Pronto4GLTrainer(persist_directory=persist_dir)
        result = trainer.train(code_directory)
        
        if result["status"] == "success":
            click.echo(f"Training completed successfully!")
            click.echo(f"Documents processed: {result['documents_processed']}")
            click.echo(f"Total chunks created: {result['chunks_created']}")
        else:
            click.echo(f"Training failed: {result['error']}", err=True)
            
    except Exception as e:
        click.echo(f"Error during training: {str(e)}", err=True)

if __name__ == '__main__':
    train()
