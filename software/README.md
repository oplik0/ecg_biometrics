# prototyp biometrii opartej o EKG

## Wstęp

Obecnie jest to prototyp - działa, ale dokładność nie jest najwyższa.
W folderze znajdują się dwa pliki - prototyp modelu w formie Jupyter Notebook, czyli kod który wykorzystywałem do treningu, oraz demo - prosty program który bierze wagi z wytrenowanego modelu i folder z plikami z danymi, po czym dla każdego pliku (obecnie dla uproszczenia sprawdzania korzysta tylko z plików których nazwy się kończą na `_SIG_II` - w zbiorze danych który wykorzystałem znajdowały się także inne dane poza sygnałami; pliki powinny być w formacie `.npy`) sprawdza czy model uważa, że należy do "celu".

Model w folderze (`model.h5`) wytrenowany jest na kolekcji 2-elektrodowych EKG z Physionetu: https://www.kaggle.com/nelsonsharma/ecg-lead-2-dataset-physionet-open-access

## użycie

`.\ekg_demo.py -m <ścieżka do pliku z modelem> -d <ścieżka do folderu z danymi>`

Opcjonalnie można jeszcze dodać argument `-c` by zdefiniować pewność jaką model musi mieć by uznać plik za należący do celu.

## wymagania

Projekt wykorzystuje biblioteki Tensorflow (2.4.1), Numpy (1.19.5), Scipy (1.5.4) oraz keras-tcn (3.4.0)

## Prototyp i demo na Kaggle

Zarówno prototyp jak i program demo zostały wykonane z użyciem Kaggle. Można więc je sprawdzić bez konieczności pobierania bazy danych samemu:
- prototyp: https://www.kaggle.com/opliko/ecg-biometrics
- demo: https://www.kaggle.com/opliko/ecg-demo (ta wersja ma hardcodowane ścieżki do danych z Kaggle)

## Hardware

Projekt wykorzystuje moduł z Kendryte K210 (Maix BiT), konwerter analogowo-cyfrrowy (ADS1115) i czujnik AD8232 do przetwarzania sygnału z EKG.

Plik `ekg_biometrics.py` powinien być wgrany na moduł jako `boot.py`. Dodatkowo należy wgrać bibliotekę [ADS1x015](https://github.com/robert-hh/ads1x15/blob/master/ads1x15.py) do obsługi konwertera analogowo cyfrowego.

Demo na hardwarze wykrozystuje prosty interfejs konsolowy. Planem było napisać coś znacznie bardziej zaawansowanego, do tego w Rust i idealnie frameworku Trussed, ale przez brak czasu (zabierany przez praktyki zawodowe, szkołę i inne konkursy - np. WorldSkills Poland) to wszystko co byłem w stanie zrobić