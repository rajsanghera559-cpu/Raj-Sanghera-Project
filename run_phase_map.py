import os
import numpy as np
import pandas as pd


def extract_params(folder):
    try:
        parts = folder.split("_")

        omega = None
        A = None

        for i, p in enumerate(parts):
            if p == "omega":
                omega = float(parts[i + 1])
            if p == "A":
                A = float(parts[i + 1])

        return omega, A
    except:
        return None, None


def load_energy(path):
    file = os.path.join(path, "energy.csv")

    if not os.path.exists(file):
        return None

    df = pd.read_csv(file)

    numeric = df.select_dtypes(include=[np.number])

    if numeric.shape[1] == 0:
        return None

    return numeric.iloc[:, 0].values


def phi(signal):
    signal = np.asarray(signal)

    if len(signal) < 5:
        return np.nan

    return np.var(signal) / (np.abs(np.mean(signal)) + 1e-9)


def phi2(signal):
    signal = np.asarray(signal)

    if len(signal) < 5:
        return np.nan

    rms = np.sqrt(np.mean(signal**2))

    return np.std(signal) / (rms + 1e-9)


def main():
    base = "outputs"
    print("Scanning:", base)

    folders = [f for f in os.listdir(base)
               if os.path.isdir(os.path.join(base, f))]

    print("Found runs:", len(folders))

    results = []

    for f in folders:
        print("\nProcessing:", f)

        path = os.path.join(base, f)

        omega, A = extract_params(f)
        print(" omega:", omega, "A:", A)

        signal = load_energy(path)
        print(" signal loaded:", signal is not None)

        if signal is None:
            continue

        p1 = phi(signal)
        p2 = phi2(signal)

        print(" Phi :", p1)
        print(" Phi2:", p2)

        results.append([omega, A, p1, p2])

    df = pd.DataFrame(results, columns=["omega", "A", "Phi", "Phi2"])
    df.to_csv("phase_map.csv", index=False)

    print("\nSaved: phase_map.csv")


if __name__ == "__main__":
    main()