using System;
using System.IO;
using System.Text;

// CTPATCH1: copy ranges from the player's original UMD, literals, and zero padding.
public static class ChaosThaiDelta
{
    static void Transfer(Stream source, Stream target, long count, byte[] buffer)
    {
        while (count > 0)
        {
            int read = source.Read(buffer, 0, (int)Math.Min(count, buffer.Length));
            if (read == 0) throw new EndOfStreamException("Truncated patch or source.");
            target.Write(buffer, 0, read);
            count -= read;
        }
    }

    public static void Apply(string original, string patch, string output, long expectedSize)
    {
        using (var source = File.OpenRead(original))
        using (var input = File.OpenRead(patch))
        using (var reader = new BinaryReader(input))
        using (var target = new FileStream(output, FileMode.CreateNew, FileAccess.Write))
        {
            if (Encoding.ASCII.GetString(reader.ReadBytes(8)) != "CTPATCH1")
                throw new InvalidDataException("Invalid patch header.");
            byte[] buffer = new byte[4 * 1024 * 1024];
            byte[] zeros = new byte[4096];
            while (true)
            {
                byte op = reader.ReadByte();
                if (op == 0)
                {
                    if (input.Position != input.Length || target.Length != expectedSize)
                        throw new InvalidDataException("Invalid patch end or output size.");
                    break;
                }
                long offset = op == 1 ? reader.ReadInt64() : 0;
                if (op < 1 || op > 3) throw new InvalidDataException("Unknown patch operation.");
                long count = reader.ReadUInt32();
                if (count > expectedSize - target.Position)
                    throw new InvalidDataException("Patch exceeds expected output size.");
                if (op == 1)
                {
                    if (offset < 0 || offset > source.Length - count)
                        throw new InvalidDataException("Copy outside original archive.");
                    source.Position = offset;
                    Transfer(source, target, count, buffer);
                }
                else if (op == 2) Transfer(input, target, count, buffer);
                else
                {
                    while (count > 0)
                    {
                        int size = (int)Math.Min(count, zeros.Length);
                        target.Write(zeros, 0, size);
                        count -= size;
                    }
                }
            }
        }
    }
}
