import contract_info as cf
# Импорт модуля с информацией о контракте, такой как адрес и ABI
from web3 import Web3
# Импорт класса Web3 для взаимодействия с Ethereum
from web3.middleware import geth_poa_middleware
# Импорт промежуточного ПО для работы с Geth POA (Proof of Authority)
# Создание экземпляра Web3 для подключения к Ethereum узлу
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
# Внедрение промежуточного ПО для корректной работы с Geth, использующим POA
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
# Создание объекта контракта с использованием адреса и ABI из импортированного модуля
contract = w3.eth.contract(address=cf.CONTRACT_ADDRESS, abi=cf.ABI)
# Получение списка аккаунтов, доступных в узле Ethereum
accounts = w3.eth.accounts
# account = w3.eth.account.create()
from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("index.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
     if request.method == 'POST':
        password = request.form.get('password') # Запрос пароля у пользователя
        errors = []
        if password is None:
            errors.append("Пожалуйста, введите пароль")
        elif len(password) < 12:
            errors.append("Пароль должен быть не менее 12 символов")
        elif not any(c.isdigit() for c in password):
            errors.append("Пароль должен содержать хотя бы одну цифру")
        elif not any(c for c in password if c in "!@#$%^&*()_-+=<>?,./"):
            errors.append("Пароль должен содержать специальные символы")
        elif "Password12345!" in password.lower() or "Qwerty1))))" in password.lower():
            errors.append("Избегайте общих шаблонов в пароле")
        elif not any(c.isupper() for c in password):
            errors.append("Пароль должен содержать хотя бы одну заглавную букву")
        elif not any(c.islower() for c in password):
            errors.append("Пароль должен содержать хотя бы одну строчную букву")

        if errors:
            return render_template("register.html", errors=errors)
        else:
            account = w3.geth.personal.new_account(password)
            key = account
            return render_template("register.html", key=key)
     return render_template("register.html", errors=None)

@app.route('/authorize', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        public_key = request.form.get('public_key')
        password = request.form.get('password')
        try:
            w3.geth.personal.unlock_account(public_key, password)
            account = public_key
            print("Авторизация прошла успешно")
            return redirect(url_for('about', account=account))
        except Exception as e:
            return render_template('authorize.html',error=str(e))
    else:
        return render_template('authorize.html',error=str(e))

@app.route('/about/<account>', methods=['GET', 'POST'])
def about(account):
    estates = contract.functions.getEstate().call()
    ads = contract.functions.getAds().call()
    balance = contract.functions.getBalanceUSER(account).call()
    if request.method == 'POST':
        type_value = request.form.get('type')
        if type_value == 'balance':
            return redirect(url_for('balance', account=account))
        if type_value == 'withdraw':
            return redirect(url_for('withdraw', account=account))
        if type_value == 'create_estate':
            return redirect(url_for('create_estate', account=account))
        if type_value == 'status_estate':
            return redirect(url_for('status_estate', account=account))
        if type_value == 'create_ad':
            return redirect(url_for('create_ad', account=account))
        if type_value == 'status_ad':
            return redirect(url_for('status_ad', account=account))
        if type_value == 'buy_estate':
            return redirect(url_for('buy_estate', account=account))
        if type_value == 'Userbalance':
            return redirect(url_for('Userbalance', account=account))
        if type_value == 'deposit':
            return redirect(url_for('deposit', account=account))
    else:
        return render_template("base.html", account=account, estates=estates, ads=ads, balance=balance)

@app.route('/about/<account>/balance/', methods=['GET', 'POST'])
def balance(account):
    if request.method == 'POST':
        public_key = str(request.form.get('public_key'))
        try:
            balance = contract.functions.getBalanceUSER(public_key).call({
                'from': account
            })
            return render_template('balance.html',balance=balance, account=account)
        except Exception as e:
            return render_template('balance.html',error=str(e), account=account)
    else:
        return render_template('balance.html')

@app.route('/about/<account>/withdraw/', methods=['GET', 'POST'])
def withdraw(account):
    if request.method == 'POST':
        amount = request.form.get('amount')
        try:
            amount = (int(amount))
            tx_hash = contract.functions.withDraw(amount).transact({
                'from': account
            })
            return render_template('withdraw.html', tx_hash=tx_hash.hex(), account=account)
        except Exception as e:
            return render_template('withdraw.html', error=str(e), account=account)
    else:
        return render_template('withdraw.html')

@app.route('/about/<account>/deposit/', methods=['GET', 'POST'])
def deposit(account):
    if request.method == 'POST':
        value = request.form.get('value')
        try:
            tx_hash = contract.functions.deposit().transact({
                'from': account,
                'value': value
            })
            return render_template('deposit.html', tx_hash=tx_hash.hex(), account=account)
        except Exception as e:
            return render_template('deposit.html', error=str(e), account=account)
    else:
        return render_template('deposit.html')

@app.route('/about/<account>/create_estate/', methods=['GET', 'POST'])
def create_estate(account):
    if request.method == 'POST':
        estate_address = request.form.get('estate_address')
        size = request.form.get('size')
        es_type = request.form.get('es_type')
        try:
            size = (int(size))
            es_type = (int(es_type))
            tx_hash = contract.functions.createEstate(size, estate_address, es_type).transact({
                'from': account,
            })
            return render_template('create_estate.html', tx_hash=tx_hash.hex(), account=account)
        except Exception as e:
            return render_template('create_estate.html', error=str(e), account=account)
    else:
        return render_template('create_estate.html')

@app.route('/about/<account>/status_estate/', methods=['GET', 'POST'])
def status_estate(account):
    if request.method == 'POST':
        id = request.form.get('id')
        try:
            tx_hash = contract.functions.statusEstate(id).transact({
                'from': account,
            })
            return render_template('status_estate.html', tx_hash=tx_hash.hex(), account=account)
        except Exception as e:
            return render_template('status_estate.html', error=str(e), account=account)
    else:
        return render_template('status_estate.html')

@app.route('/about/<account>/create_ad/', methods=['GET', 'POST'])
def create_ad(account):
    if request.method == 'POST':
        id_estate = request.form.get('id_estate')
        price = request.form.get('price')
        try:
            id_estate = (int(id_estate))
            price = (int(price))
            tx_hash = contract.functions.createAd(price, id_estate).transact({
                'from': account,
            })
            return render_template('create_ad.html', tx_hash=tx_hash.hex(), account=account)
        except Exception as e:
            return render_template('create_ad.html', error=str(e), account=account)
    else:
        return render_template('create_ad.html')

@app.route('/about/<account>/status_ad/', methods=['GET', 'POST'])
def status_ad(account):
    if request.method == 'POST':
        id = request.form.get('id')
        try:
            tx_hash = contract.functions.statusAd(id).transact({
                'from': account,
            })
            return render_template('status_ad.html', tx_hash=tx_hash.hex(), account=account)
        except Exception as e:
            return render_template('status_ad.html', error=str(e), account=account)
    else:
        return render_template('status_ad.html')

@app.route('/about/<account>/buy_estate/', methods=['GET', 'POST'])
def buy_estate(account):
    if request.method == 'POST':
        id_ad = request.form.get('id_ad')
        buyer_id = request.form.get('buyer_id')
        try:
            id_ad = (int(id_ad))
            tx_hash = contract.functions.buyEstate(id_ad, buyer_id).transact({
                'from': account,
            })
            return render_template('buy_estate.html', tx_hash=tx_hash.hex(), account=account)
        except Exception as e:
            return render_template('buy_estate.html', error=str(e), account=account)
    else:
        return render_template('buy_estate.html')


@app.route('/about/<account>/Userbalance/', methods=['GET', 'POST'])
def Userbalance(account):
    if request.method == 'POST':
        value = request.form.get('value')
        if not value:
            return render_template('Userbalance.html', error="Значение не может быть пустым")
        try:
            tx_hash = w3.eth.send_transaction({
                'from': w3.eth.coinbase,
                'to': account,
                'value': value
            })
            return render_template('Userbalance.html', tx_hash=tx_hash, account=account)
        except Exception as e:
            return render_template('Userbalance.html', error=str(e), account=account)
    else:
        return render_template('Userbalance.html')

if __name__ == "__main__":
    app.run(debug=True)
