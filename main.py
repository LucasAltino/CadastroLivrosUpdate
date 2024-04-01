from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave_da_boa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/livros'
db = SQLAlchemy(app)


class Livro(db.Model):
    id_livro = db.Column(db.Integer, primary_key=True, autoincrement=True)
    titulo = db.Column(db.String(100))
    autor = db.Column(db.String(254))
    ano_publicacao = db.Column(db.Integer)


class Usuario(db.Model):
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(254))
    senha = db.Column(db.String(100))


@app.route('/')
def index():
    livros = Livro.query.all()
    return render_template('cadastro_livros.html', outro=livros)


@app.route('/novo')
def novo():
    return render_template('novo.html', titulo='Novo Livro')


@app.route('/criar', methods=['POST'])
def criar():
    titulo = request.form['titulo']
    autor = request.form['autor']
    ano_publicacao = request.form['ano_publicacao']

    livro = Livro.query.filter_by(titulo=titulo).first()
    if livro:
        flash("Livro já existente!")
        return redirect(url_for('novo'))

    novo_livro = Livro(titulo=titulo, autor=autor, ano_publicacao=ano_publicacao)

    db.session.add(novo_livro)
    db.session.commit()
    arquivo = request.files['arquivo']
    arquivo.save(f'uploads/capa{novo_livro.id_livro}.jpg')
    return redirect(url_for('index'))


@app.route('/editar/<int:identifier>')
def editar(identifier):
    livro = Livro.query.filter_by(id_livro=identifier).first()
    return render_template('editar.html', titulo='Editando livro', livro=livro)


@app.route('/atualizar', methods=['POST'])
def atualizar():
    livro = Livro.query.filter_by(id_livro=request.form['id']).first()
    livro.titulo = request.form['titulo']
    livro.autor = request.form['autor']
    livro.ano_publicacao = request.form['ano_publicacao']

    db.session.add(livro)
    db.session.commit()

    return redirect(url_for('index'))


@app.route('/deletar/<int:identifier>')
def deletar(identifier):
    Livro.query.filter_by(id_livro=identifier).delete()
    db.session.commit()
    flash('Livro excluido com sucesso.')
    return redirect(url_for('index'))


@app.route('/uploads/<nome_arquivo>')
def imagem(nome_arquivo):
    return send_from_directory('uploads', nome_arquivo)


@app.route('/login')
def login_form():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    senha = request.form.get('senha')
    user = Usuario.query.filter_by(email=email).first()

    if user and senha == user.senha:
        return redirect(url_for('index'))
    else:
        flash('Email ou senha incorretos', 'error')
        return redirect(url_for('login_form'))


@app.route('/novo_user')
def novo_user():
    return render_template('novo_usuario.html', titulo='Novo Usuário')


@app.route('/criar_user', methods=['POST'])
def criar_user():
    email = request.form['email']
    senha = request.form['senha']
    user = Usuario.query.filter_by(email=email).first()
    if user:
        flash('Usuário já existe', 'error')
        return redirect(url_for('novo_user'))
    else:
        novo_usuario = Usuario(email=email, senha=senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash('Usuário cadastrado com sucesso', 'success')
        return redirect(url_for('login_form'))


if __name__ == '__main__':
    app.run(debug=True)
