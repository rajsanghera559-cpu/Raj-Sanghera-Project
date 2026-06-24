if __name__ == "__main__":
    main()

    import pandas as pd

    df = pd.read_csv("phase_map.csv")

    grouped = df.groupby(["omega", "A"])

    for (omega, A), g in grouped:
        if g["N"].nunique() > 1:
            sample = g.sort_values("N")[["N", "Phi", "Phi2"]]

            print("\nTest pair:")
            print("omega =", omega, "A =", A)
            print(sample)

            break