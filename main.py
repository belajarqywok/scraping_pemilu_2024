import asyncio
from kpu import KPU
from utils import directory, write_csv, save_image

async def main():
    kpu = KPU()

    directory(path = f'./cform/')
    directory(path = f'./datasets/')

    # Province
    provinces = await kpu.get_provinces()
    for _, v_province in enumerate(provinces.get('contents')):
        province_name = v_province['nama']
        province_code = v_province['kode']

        # City
        cities = await kpu.get_cities(prov_id=province_code)
        for _, v_city in enumerate(cities.get('contents')):
            city_name = v_city['nama']
            city_code = v_city['kode']

            # Kecamatan
            kecamatan = await kpu.get_kec(prov_id=province_code, city_id=city_code)
            for _, v_kecamatan in enumerate(kecamatan.get('contents')):
                kecamatan_name = v_kecamatan['nama']
                kecamatan_code = v_kecamatan['kode']

                # Kelurahan
                kelurahan = await kpu.get_kel(prov_id=province_code, city_id=city_code, kec_id=kecamatan_code)
                for _, v_kelurahan in enumerate(kelurahan.get('contents')):
                    kelurahan_name = v_kelurahan['nama']
                    kelurahan_code = v_kelurahan['kode']

                    # TPS
                    tps = await kpu.get_tps(prov_id=province_code, city_id=city_code,
                        kec_id=kecamatan_code, kel_id=kelurahan_code)

                    for _, v_tps in enumerate(tps.get('contents')):
                        tps_name = v_tps['nama']
                        tps_code = v_tps['kode']

                        tps_data = await kpu.get_tps_data(
                            prov_id=province_code,
                            city_id=city_code,
                            kec_id=kecamatan_code,
                            kel_id=kelurahan_code,
                            tps_id=tps_code
                        )

                        fields = [
                            'Province_ID',
                            'Province_Name',
                            'City_ID',
                            'City_Name',
                            'Kecamatan_ID',
                            'Kecamatan_Name',
                            'Kelurahan_ID',
                            'Kelurahan_Name',
                            'TPS_ID',
                            'TPS_Name',
                            'DPT',
                            'DPTb',
                            'DPK',
                            'Paslon_01',
                            'Paslon_02',
                            'Paslon_03',
                            'Valid_Vote',
                            'Invalid_Vote',
                            'Total_Vote',
                            'Status'
                        ]

                        administrative = tps_data['contents']['administrasi']
                        if administrative is None:
                          DPT, DPTb, DPK = 0, 0, 0
                          valid_vote, invalid_vote, total_vote = 0, 0, 0
                        else:
                          DPT  = administrative['pengguna_dpt_j']
                          DPTb = administrative['pengguna_dptb_j']
                          DPK  = administrative['pengguna_non_dpt_j']

                          valid_vote = administrative['pengguna_non_dpt_j']
                          invalid_vote = administrative['pengguna_non_dpt_j']
                          total_vote = administrative['pengguna_non_dpt_j']


                        chart = tps_data['contents']['chart']
                        if chart is None:
                            paslon_1, paslon_2, paslon_3 = 0, 0, 0
                            status = 'PROCESS'
                        else:
                            pres_data = sum([0 if v is None else v for v in chart.values()])
                            if pres_data == valid_vote and valid_vote + invalid_vote == total_vote:
                                paslon_1 = chart.get('100025', 0)
                                paslon_2 = chart.get('100026', 0)
                                paslon_3 = chart.get('100027', 0)
                                status = 'INVALID'
                            else:
                                paslon_1 = chart.get('100025', 0)
                                paslon_2 = chart.get('100026', 0)
                                paslon_3 = chart.get('100027', 0)
                                status = 'VALID'

                        data = {
                              'Province_ID': province_code,
                              'Province_Name': province_name,
                              'City_ID': city_code,
                              'City_Name': city_name,
                              'Kecamatan_ID': kecamatan_code,
                              'Kecamatan_Name': kecamatan_name,
                              'Kelurahan_ID': kelurahan_code,
                              'Kelurahan_Name': kelurahan_name,
                              'TPS_ID': tps_code,
                              'TPS_Name': tps_name,
                              'DPT': DPT,
                              'DPTb': DPTb,
                              'DPK': DPK,
                              'Paslon_01': paslon_1,
                              'Paslon_02': paslon_2,
                              'Paslon_03': paslon_3,
                              'Valid_Vote': valid_vote,
                              'Invalid_Vote': invalid_vote,
                              'Total_Vote': total_vote,
                              'Status': status
                          }

                        images = tps_data['contents']['images']
                        if images is not None:
                            tasks = []
                            for i, img in enumerate(images, start=1):
                                key = f'Image_C-Hasil_{i}'
                                fields.append(key)
                                data[key] = img
                                if img is not None:
                                    cform_path = f'./cform/{tps_code}/'
                                    directory(cform_path)
                                    task = asyncio.create_task(save_image(cform_path, img))
                                    tasks.append(task)
                            await asyncio.gather(*tasks)


                        write_csv(
                          path = f'./datasets/{province_name}.csv',
                          fields = fields,
                          data = data
                        )

                        print(
                          f"[ {province_name}:{city_name}:{kecamatan_name}:{kelurahan_name}:{tps_name} ] {paslon_1} | {paslon_2} | {paslon_3}"
                        )

        # ---

asyncio.run(main())