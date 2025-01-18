import click
import requests
import sys
from pathlib import Path

@click.group()
def main():
    """Pronto 4GL Assistant CLI"""
    pass

@main.command()
@click.argument('file', type=click.Path(exists=True))
def upload(file):
    """Upload a Pronto 4GL document"""
    try:
        with open(file, 'rb') as f:
            files = {'file': f}
            response = requests.post('http://localhost:8000/api/documents', files=files)
            if response.status_code == 200:
                click.echo(f"Successfully uploaded {file}")
                click.echo(response.json())
            else:
                click.echo(f"Error uploading file: {response.text}", err=True)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

@main.command()
@click.argument('code', type=str)
def analyze(code):
    """Analyze Pronto 4GL code"""
    try:
        response = requests.post('http://localhost:8000/api/analyze', 
                               json={'code': code})
        if response.status_code == 200:
            click.echo("Analysis Results:")
            click.echo(response.json())
        else:
            click.echo(f"Error analyzing code: {response.text}", err=True)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

@main.command()
@click.argument('description', type=str)
def generate(description):
    """Generate Pronto 4GL code"""
    try:
        response = requests.post('http://localhost:8000/api/generate',
                               json={'description': description})
        if response.status_code == 200:
            click.echo("Generated Code:")
            click.echo(response.json())
        else:
            click.echo(f"Error generating code: {response.text}", err=True)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)

if __name__ == '__main__':
    main()
