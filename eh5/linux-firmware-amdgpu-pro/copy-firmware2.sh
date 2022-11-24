#!/bin/sh
# SPDX-License-Identifier: GPL-2.0
#
# Copy firmware files based on WHENCE list
#

verbose=:
prune=no
compress=no
prefix=

while test $# -gt 0; do
    case $1 in
        -v | --verbose)
            verbose=echo
            shift
            ;;

        -P | --prune)
            prune=yes
            shift
            ;;

        -C | --compress)
            compress=yes
            shift
            ;;

        --prefix)
            prefix="$2"
            shift 2
            ;;

        *)
            if test "x$destdir" != "x"; then
                echo "ERROR: unknown command-line options: $@"
                exit 1
            fi

            destdir="$1"
            shift
            ;;
    esac
done

if test "x$compress" = "xyes"; then
    cmpxtn=.xz
    grep "^File: $prefix" WHENCE | sed -e's/^File: *//g' -e's/"//g' | while read f; do
       test -f "$f" || continue
       $verbose "compressing $f"
       xz -C crc32 "$f"
    done
fi

grep "^File: $prefix" WHENCE | sed -e's/^File: *//g' -e's/"//g' | while read f; do
    test -f "$f$cmpxtn" || continue
    $verbose "copying file $f$cmpxtn"
    install -d $destdir/$(dirname "$f$cmpxtn")
    cp -d "$f$cmpxtn" $destdir/"$f$cmpxtn"
done

grep -E "^Link: $prefix" WHENCE | sed -e's/^Link: *//g' -e's/-> //g' | while read f d; do
    if test -L "$f$cmpxtn"; then
        test -f "$destdir/$f$cmpxtn" && continue
        $verbose "copying link $f$cmpxtn"
        install -d $destdir/$(dirname "$f$cmpxtn")
        cp -d "$f" $destdir/"$f"

        if test "x$d" != "x"; then
            target=`readlink "$f$cmpxtn"`

            if test "x$target" != "x$d"; then
                $verbose "WARNING: inconsistent symlink target: $target != $d"
            else
                if test "x$prune" != "xyes"; then
                    $verbose "WARNING: unneeded symlink detected: $f$cmpxtn"
                else
                    $verbose "WARNING: pruning unneeded symlink $f$cmpxtn"
                    rm -f "$f$cmpxtn"
                fi
            fi
        else
            $verbose "WARNING: missing target for symlink $f$cmpxtn"
        fi
    else
        $verbose "creating link $f$cmpxtn -> $d$cmpxtn"
        install -d $destdir/$(dirname "$f$cmpxtn")
        ln -sf "$d$cmpxtn" "$destdir/$f$cmpxtn"
    fi
done

exit 0

# vim: et sw=4 sts=4 ts=4
