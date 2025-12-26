"""
Flask CLI 명령어

플랫폼 관리 명령어를 제공합니다.
"""
import click
from flask.cli import with_appcontext


@click.command('create-superadmin')
@click.option('--username', prompt=True, help='Superadmin username')
@click.option('--email', prompt=True, help='Superadmin email')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Superadmin password')
@with_appcontext
def create_superadmin(username, email, password):
    """플랫폼 마스터 관리자 계정 생성"""
    from app.database import db
    from app.models import User

    # 중복 검사
    if User.query.filter_by(username=username).first():
        click.echo(click.style(f'Error: Username "{username}" already exists', fg='red'))
        return

    if User.query.filter_by(email=email).first():
        click.echo(click.style(f'Error: Email "{email}" already exists', fg='red'))
        return

    # Superadmin 생성
    user = User(
        username=username,
        email=email,
        account_type=User.ACCOUNT_PLATFORM,
        role=User.ROLE_ADMIN,
        is_superadmin=True,
        company_id=None,
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    click.echo(click.style(f'Superadmin "{username}" created successfully!', fg='green'))
    click.echo(f'  - Email: {email}')
    click.echo(f'  - Account Type: {user.account_type}')
    click.echo(f'  - Is Superadmin: {user.is_superadmin}')


@click.command('list-superadmins')
@with_appcontext
def list_superadmins():
    """플랫폼 마스터 관리자 목록 조회"""
    from app.models import User

    superadmins = User.query.filter_by(is_superadmin=True).all()

    if not superadmins:
        click.echo('No superadmins found.')
        return

    click.echo(f'Found {len(superadmins)} superadmin(s):')
    for user in superadmins:
        status = click.style('active', fg='green') if user.is_active else click.style('inactive', fg='red')
        click.echo(f'  - {user.username} ({user.email}) [{status}]')


def register_cli_commands(app):
    """Flask 앱에 CLI 명령어 등록"""
    app.cli.add_command(create_superadmin)
    app.cli.add_command(list_superadmins)
