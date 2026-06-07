from django.core.management.base import BaseCommand

from homepage.address_data import (
    fetch_from_cas,
    save_communes,
    save_provinces,
)


class Command(BaseCommand):
    help = (
        'Tải dữ liệu tỉnh/thành phố và xã/phường từ CAS Address Kit '
        'và lưu vào homepage/static/data/address/'
    )

    def handle(self, *args, **options):
        self.stdout.write('Đang tải danh sách tỉnh/thành phố...')
        provinces_data = fetch_from_cas('provinces')
        provinces = provinces_data.get('provinces', [])
        save_provinces(provinces_data)
        self.stdout.write(self.style.SUCCESS(f'Đã lưu {len(provinces)} tỉnh/thành phố'))

        total_communes = 0
        for province in provinces:
            code = province['code']
            name = province['name']
            self.stdout.write(f'  → {code}: {name}')
            communes_data = fetch_from_cas(f'provinces/{code}/communes')
            communes = communes_data.get('communes', [])
            save_communes(code, communes_data)
            total_communes += len(communes)

        self.stdout.write(
            self.style.SUCCESS(
                f'Hoàn tất: {len(provinces)} tỉnh/thành phố, '
                f'{total_communes} xã/phường'
            )
        )
