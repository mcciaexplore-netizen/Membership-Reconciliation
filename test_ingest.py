import traceback
from src.ingest import load_config, load_bank_statement, load_backend_data

def main():
    config = load_config('config/config.yaml')
    try:
        print('Loading bank...')
        bank = load_bank_statement('public/26-27 MEMBERSHIP FEES.xls', config)
        print('Bank columns:', list(bank.columns))
        print('Loading backend...')
        backend = load_backend_data('public/Membership Payment Summary 2026(Backend).xlsx', config)
        print('Backend columns:', list(backend.columns))
    except Exception as e:
        traceback.print_exc()

if __name__ == '__main__':
    main()
